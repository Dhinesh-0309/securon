"""Factory for creating IaC Scanner instances with Rule Engine integration"""

from typing import Optional
from ..rule_engine.engine import ConcreteRuleEngine
from ..interfaces.iac_scanner import IaCScanner
from .scanner import ConcreteIaCScanner


class IaCScannerFactory:
    """Factory for creating IaC Scanner instances"""
    
    @staticmethod
    def create_scanner(rule_engine: Optional[ConcreteRuleEngine] = None) -> IaCScanner:
        """Create an IaC Scanner instance with optional Rule Engine integration"""
        scanner = ConcreteIaCScanner()
        
        if rule_engine:
            # Apply active rules from the Rule Engine
            import asyncio
            
            async def apply_rules():
                try:
                    active_rules = await rule_engine.get_active_rules()
                    scanner.apply_rules(active_rules)
                except Exception as e:
                    # Log error but continue with default rules
                    print(f"Warning: Failed to load rules from Rule Engine: {e}")
            
            # Run the async function to apply rules
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, create a task
                    asyncio.create_task(apply_rules())
                else:
                    # If not in async context, run it
                    loop.run_until_complete(apply_rules())
            except RuntimeError:
                # Create new event loop if none exists
                asyncio.run(apply_rules())
        
        return scanner
    
    @staticmethod
    async def create_scanner_async(rule_engine: Optional[ConcreteRuleEngine] = None) -> IaCScanner:
        """Create an IaC Scanner instance asynchronously with Rule Engine integration"""
        scanner = ConcreteIaCScanner()
        
        if rule_engine:
            try:
                active_rules = await rule_engine.get_active_rules()
                scanner.apply_rules(active_rules)
            except Exception as e:
                # Log error but continue with default rules
                print(f"Warning: Failed to load rules from Rule Engine: {e}")
        
        return scanner