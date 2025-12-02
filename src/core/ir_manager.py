import ast
import astor
import os
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

@dataclass
class CodeIR:
    """
    Intermediate Representation of code at multiple abstraction layers.
    """
    original_code: str
    l1_intent: str  # Natural language description
    l2_obfuscated: str  # Code with obfuscated variable names
    l3_llvm: Optional[str] = None  # LLVM IR (stub for now)
    
    def __hash__(self):
        return hash(self.original_code)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CodeIR':
        return cls(**data)

class IRGenerator:
    """
    Generates intermediate representations for different layers.
    """
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self._obfuscation_map = {}
        
    def generate_ir(self, code: str) -> CodeIR:
        """Generate all IR layers for given code."""
        l1_intent = self.generate_l1_intent(code)
        l2_obfuscated = self.generate_l2_obfuscated(code)
        l3_llvm = self.generate_l3_llvm(code)
        
        return CodeIR(
            original_code=code,
            l1_intent=l1_intent,
            l2_obfuscated=l2_obfuscated,
            l3_llvm=l3_llvm
        )
    
    def generate_l1_intent(self, code: str) -> str:
        """
        Generate L1: Natural language intent description using LLM.
        """
        if self.llm is None:
            return "Intent description unavailable (no LLM)"
        
        try:
            prompt = f"""You are an expert computer scientist analyzing code.

Analyze the following Python code and provide a concise description of its algorithmic intent.
Focus on WHAT it does, not HOW. Describe the time complexity if relevant.
Provide ONLY the intent description, no explanations or extra text.

Code:
{code}

Intent:"""
            intent = self.llm.complete(prompt).strip()
            return intent
        except Exception as e:
            logger.error(f"L1 intent generation failed: {e}")
            return f"Error generating intent: {str(e)}"
    
    def generate_l2_obfuscated(self, code: str) -> str:
        """
        Generate L2: Python code with completely obfuscated variable names.
        Uses deterministic mapping for consistency.
        """
        try:
            tree = ast.parse(code)
            self._obfuscation_map = {}
            obfuscator = VariableObfuscator(self._obfuscation_map)
            obfuscated_tree = obfuscator.visit(tree)
            ast.fix_missing_locations(obfuscated_tree)
            return astor.to_source(obfuscated_tree)
        except Exception as e:
            logger.error(f"L2 obfuscation failed: {e}")
            return code  # Fallback to original
    
    def generate_l3_llvm(self, code: str) -> Optional[str]:
        """
        Generate L3: LLVM IR (stubbed for now).
        Future: Could use tools like numba or compile via ctypes.
        """
        # Stub implementation
        return "# LLVM IR generation not yet implemented"
    
    def regenerate_code_from_l1(self, intent: str) -> str:
        """
        Regenerate Python code from L1 intent using LLM.
        """
        if self.llm is None:
            raise ValueError("LLM required for L1 -> code regeneration")
        
        prompt = f"""You are an expert Python programmer.

Implement the following algorithmic intent in efficient, production-ready Python code.
- Use the most efficient algorithm and data structures
- Return ONLY the Python code, no markdown formatting, no explanations

Intent:
{intent}

Python Code:"""
        code = self.llm.complete(prompt).strip()
        
        # Clean up markdown formatting if present
        if code.startswith("```python"):
            code = code.split("```python")[1]
        elif code.startswith("```"):
            code = code.split("```")[1]
        if code.endswith("```"):
            code = code.rsplit("```", 1)[0]
        
        return code.strip()
    
    def deobfuscate_l2(self, obfuscated_code: str) -> str:
        """
        Attempt to reverse obfuscation (best effort).
        Note: This is lossy if original mapping is lost.
        """
        # For now, just return as-is since we don't maintain reverse mapping
        return obfuscated_code

class VariableObfuscator(ast.NodeTransformer):
    """
    AST transformer that completely obfuscates variable names.
    """
    def __init__(self, mapping: Dict[str, str]):
        self.mapping = mapping
        self.counter = 0
        # Builtins and keywords to preserve
        self.preserve = set(dir(__builtins__)) | {
            'True', 'False', 'None', 'self', 'cls'
        }
    
    def _get_obfuscated_name(self, original: str) -> str:
        if original in self.preserve:
            return original
        if original not in self.mapping:
            self.mapping[original] = f"var_{self.counter}"
            self.counter += 1
        return self.mapping[original]
    
    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Load, ast.Del)):
            node.id = self._get_obfuscated_name(node.id)
        return node
    
    def visit_arg(self, node):
        node.arg = self._get_obfuscated_name(node.arg)
        return node
    
    def visit_FunctionDef(self, node):
        node.name = self._get_obfuscated_name(node.name)
        return self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        node.name = self._get_obfuscated_name(node.name)
        return self.generic_visit(node)

class IRSerializer:
    """
    Serializes and deserializes CodeIR objects to/from disk.
    """
    @staticmethod
    def save_ir(code_ir: CodeIR, directory: str, prefix: str = ""):
        """
        Save CodeIR to disk with separate files for each layer.
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save L1 intent
        with open(os.path.join(directory, f"{prefix}l1_intent.txt"), 'w') as f:
            f.write(code_ir.l1_intent)
        
        # Save L2 obfuscated code
        with open(os.path.join(directory, f"{prefix}l2_obfuscated.py"), 'w') as f:
            f.write(code_ir.l2_obfuscated)
        
        # Save L3 LLVM (stub)
        if code_ir.l3_llvm:
            with open(os.path.join(directory, f"{prefix}l3_llvm.ll"), 'w') as f:
                f.write(code_ir.l3_llvm)
        
        # Save original code for reference
        with open(os.path.join(directory, f"{prefix}original.py"), 'w') as f:
            f.write(code_ir.original_code)
        
        # Save metadata
        metadata = {
            'code_hash': hashlib.md5(code_ir.original_code.encode()).hexdigest(),
            'has_llvm': code_ir.l3_llvm is not None
        }
        with open(os.path.join(directory, f"{prefix}metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
    
    @staticmethod
    def load_ir(directory: str, prefix: str = "") -> CodeIR:
        """
        Load CodeIR from disk.
        """
        with open(os.path.join(directory, f"{prefix}original.py"), 'r') as f:
            original_code = f.read()
        
        with open(os.path.join(directory, f"{prefix}l1_intent.txt"), 'r') as f:
            l1_intent = f.read()
        
        with open(os.path.join(directory, f"{prefix}l2_obfuscated.py"), 'r') as f:
            l2_obfuscated = f.read()
        
        l3_llvm = None
        llvm_path = os.path.join(directory, f"{prefix}l3_llvm.ll")
        if os.path.exists(llvm_path):
            with open(llvm_path, 'r') as f:
                l3_llvm = f.read()
        
        return CodeIR(
            original_code=original_code,
            l1_intent=l1_intent,
            l2_obfuscated=l2_obfuscated,
            l3_llvm=l3_llvm
        )
