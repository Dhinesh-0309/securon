"""Terraform file parsing and AST analysis"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import hcl2

from ..interfaces.core_types import TerraformResource


class TerraformParseError(Exception):
    """Exception raised for Terraform parsing errors"""
    pass


class TerraformParser:
    """Parser for Terraform files with AST analysis capabilities"""
    
    def __init__(self):
        self.resource_pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{')
        self.data_pattern = re.compile(r'data\s+"([^"]+)"\s+"([^"]+)"\s*{')
    
    async def parse_file(self, file_path: str) -> List[TerraformResource]:
        """Parse a Terraform file and extract resources"""
        try:
            if file_path.endswith('.tf.json'):
                return await self._parse_json_file(file_path)
            else:
                return await self._parse_hcl_file(file_path)
        except Exception as e:
            raise TerraformParseError(f"Failed to parse {file_path}: {str(e)}")
    
    async def _parse_hcl_file(self, file_path: str) -> List[TerraformResource]:
        """Parse a .tf HCL file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse HCL content
            parsed = hcl2.loads(content)
            
            resources = []
            
            # Extract resources
            if 'resource' in parsed:
                resource_list = parsed['resource']
                if isinstance(resource_list, list):
                    # HCL2 returns resources as a list of dictionaries
                    for resource_dict in resource_list:
                        for resource_type, resource_instances in resource_dict.items():
                            for resource_name, resource_config in resource_instances.items():
                                # Find line number by searching in original content
                                line_number = self._find_resource_line_number(
                                    content, resource_type, resource_name
                                )
                                
                                terraform_resource = TerraformResource(
                                    type=resource_type,
                                    name=resource_name,
                                    configuration=resource_config,
                                    file_path=file_path,
                                    line_number=line_number
                                )
                                resources.append(terraform_resource)
                else:
                    # Handle dict format (older HCL parsers)
                    for resource_type, resource_instances in resource_list.items():
                        for resource_name, resource_config in resource_instances.items():
                            line_number = self._find_resource_line_number(
                                content, resource_type, resource_name
                            )
                            
                            terraform_resource = TerraformResource(
                                type=resource_type,
                                name=resource_name,
                                configuration=resource_config,
                                file_path=file_path,
                                line_number=line_number
                            )
                            resources.append(terraform_resource)
            
            # Extract data sources (treat as resources for security analysis)
            if 'data' in parsed:
                data_list = parsed['data']
                if isinstance(data_list, list):
                    # HCL2 returns data sources as a list of dictionaries
                    for data_dict in data_list:
                        for data_type, data_instances in data_dict.items():
                            for data_name, data_config in data_instances.items():
                                line_number = self._find_data_line_number(
                                    content, data_type, data_name
                                )
                                
                                terraform_resource = TerraformResource(
                                    type=f"data.{data_type}",
                                    name=data_name,
                                    configuration=data_config,
                                    file_path=file_path,
                                    line_number=line_number
                                )
                                resources.append(terraform_resource)
                else:
                    # Handle dict format (older HCL parsers)
                    for data_type, data_instances in data_list.items():
                        for data_name, data_config in data_instances.items():
                            line_number = self._find_data_line_number(
                                content, data_type, data_name
                            )
                            
                            terraform_resource = TerraformResource(
                                type=f"data.{data_type}",
                                name=data_name,
                                configuration=data_config,
                                file_path=file_path,
                                line_number=line_number
                            )
                            resources.append(terraform_resource)
            
            return resources
            
        except Exception as e:
            raise TerraformParseError(f"HCL parsing error: {str(e)}")
    
    async def _parse_json_file(self, file_path: str) -> List[TerraformResource]:
        """Parse a .tf.json file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            resources = []
            
            # Extract resources
            if 'resource' in content:
                for resource_type, resource_instances in content['resource'].items():
                    for resource_name, resource_config in resource_instances.items():
                        terraform_resource = TerraformResource(
                            type=resource_type,
                            name=resource_name,
                            configuration=resource_config,
                            file_path=file_path,
                            line_number=1  # JSON files don't have meaningful line numbers for resources
                        )
                        resources.append(terraform_resource)
            
            # Extract data sources
            if 'data' in content:
                for data_type, data_instances in content['data'].items():
                    for data_name, data_config in data_instances.items():
                        terraform_resource = TerraformResource(
                            type=f"data.{data_type}",
                            name=data_name,
                            configuration=data_config,
                            file_path=file_path,
                            line_number=1
                        )
                        resources.append(terraform_resource)
            
            return resources
            
        except json.JSONDecodeError as e:
            raise TerraformParseError(f"JSON parsing error: {str(e)}")
        except Exception as e:
            raise TerraformParseError(f"Unexpected error: {str(e)}")
    
    def _find_resource_line_number(self, content: str, resource_type: str, resource_name: str) -> int:
        """Find the line number where a resource is defined"""
        lines = content.split('\n')
        pattern = re.compile(rf'resource\s+"{re.escape(resource_type)}"\s+"{re.escape(resource_name)}"')
        
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                return i
        
        return 1  # Default to line 1 if not found
    
    def _find_data_line_number(self, content: str, data_type: str, data_name: str) -> int:
        """Find the line number where a data source is defined"""
        lines = content.split('\n')
        pattern = re.compile(rf'data\s+"{re.escape(data_type)}"\s+"{re.escape(data_name)}"')
        
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                return i
        
        return 1  # Default to line 1 if not found
    
    def validate_terraform_syntax(self, content: str) -> List[str]:
        """Validate Terraform syntax and return list of errors"""
        errors = []
        
        try:
            # Try to parse as HCL
            hcl2.loads(content)
        except Exception as e:
            errors.append(f"HCL syntax error: {str(e)}")
        
        # Additional basic validation
        if not self._validate_basic_structure(content):
            errors.append("Invalid Terraform file structure")
        
        return errors
    
    def _validate_basic_structure(self, content: str) -> bool:
        """Perform basic structural validation of Terraform content"""
        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            return False
        
        # Check for basic Terraform blocks
        has_terraform_content = bool(
            re.search(r'(resource|data|variable|output|locals|terraform)\s+', content)
        )
        
        return has_terraform_content or content.strip() == ""  # Empty files are valid