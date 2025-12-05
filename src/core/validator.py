"""
IR Validator - migrated to new domain IR system.

Provides validation for the domain IR Module, replacing the deprecated
CodeIR validation system.
"""
import logging
from typing import List
from src.domain.ir.schema import Module, FunctionDef
from src.domain.ir.validators import IRValidator, ValidationResult

logger = logging.getLogger(__name__)

class Validator:
    """
    Main validation entry point for IR validation.
    
    This class wraps the domain IRValidator to provide backward compatibility
    and additional validation logic.
    """
    
    def __init__(self):
        self.ir_validator = IRValidator()
    
    def validate(self, ir: Module) -> ValidationResult:
        """
        Validate an IR Module.
        
        Args:
            ir: The IR Module to validate
            
        Returns:
            ValidationResult with valid flag and any errors
        """
        return self.ir_validator.validate(ir)
    
    def validate_pre_mutation(self, ir: Module) -> ValidationResult:
        """Validate IR before mutation."""
        return self.validate(ir)
    
    def validate_post_mutation(self, ir: Module) -> ValidationResult:
        """Validate IR after mutation."""
        return self.validate(ir)
