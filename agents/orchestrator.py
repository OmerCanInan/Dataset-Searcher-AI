"""
Orchestrator (Manager Agent)
Coordinates all agents using LangGraph State management (A2A Protocol)
Controls workflow: Hunter -> Parser -> Light-EDA -> Normalizer -> Validator -> Final-EDA
"""

from typing import TypedDict, Optional, List, Dict, Any
import json


class ADMARState(TypedDict):
    """Shared state passed between agents (A2A Handoff Protocol)."""
    # User Input
    user_prompt: str
    
    # Hunter Output
    raw_urls: List[str]
    raw_data: Optional[str]
    
    # Parser Output
    raw_dataframe: Optional[str]  # JSON serialized
    
    # Light-EDA Output
    eda_report: Dict[str, Any]
    normalization_recipe: Dict[str, Any]
    
    # Normalizer Output
    clean_dataframe: Optional[str]  # JSON serialized
    
    # Validator Output
    quality_score: float
    validation_passed: bool
    
    # Final-EDA Output
    final_report: Dict[str, Any]
    visualizations: List[str]
    
    # Workflow Control
    current_stage: str
    error_message: Optional[str]
    retry_count: int
    max_retries: int


class OrchestratorManager:
    """
    Manages the workflow between all agents.
    Implements A2A protocol for agent handoffs via shared state.
    """
    
    def __init__(self):
        self.state: ADMARState = {
            'user_prompt': '',
            'raw_urls': [],
            'raw_data': None,
            'raw_dataframe': None,
            'eda_report': {},
            'normalization_recipe': {},
            'clean_dataframe': None,
            'quality_score': 0.0,
            'validation_passed': False,
            'final_report': {},
            'visualizations': [],
            'current_stage': 'init',
            'error_message': None,
            'retry_count': 0,
            'max_retries': 3
        }
    
    def set_user_prompt(self, prompt: str):
        """Stage 0: User provides prompt."""
        self.state['user_prompt'] = prompt
        self.state['current_stage'] = 'planning'
    
    def hunter_complete(self, urls: List[str], raw_data: str):
        """Stage 1: Hunter completes search."""
        self.state['raw_urls'] = urls
        self.state['raw_data'] = raw_data
        self.state['current_stage'] = 'extraction'
    
    def parser_complete(self, dataframe_json: str):
        """Stage 2: Parser transforms unstructured -> structured."""
        self.state['raw_dataframe'] = dataframe_json
        self.state['current_stage'] = 'discovery'
    
    def eda_discovery_complete(self, eda_report: Dict, recipe: Dict):
        """Stage 3: Light-EDA generates normalization recipe."""
        self.state['eda_report'] = eda_report
        self.state['normalization_recipe'] = recipe
        self.state['current_stage'] = 'normalization'
    
    def normalizer_complete(self, clean_df_json: str):
        """Stage 4: Normalizer standardizes data."""
        self.state['clean_dataframe'] = clean_df_json
        self.state['current_stage'] = 'validation'
    
    def validator_complete(self, quality_score: float, passed: bool):
        """Stage 5: Validator checks quality."""
        self.state['quality_score'] = quality_score
        self.state['validation_passed'] = passed
        
        if not passed and self.state['retry_count'] < self.state['max_retries']:
            self.state['retry_count'] += 1
            self.state['current_stage'] = 'planning'  # Restart search
        else:
            self.state['current_stage'] = 'analysis'
    
    def final_eda_complete(self, report: Dict, visualizations: List[str]):
        """Stage 6: Final-EDA generates analysis."""
        self.state['final_report'] = report
        self.state['visualizations'] = visualizations
        self.state['current_stage'] = 'complete'
    
    def set_error(self, error_msg: str):
        """Handle errors."""
        self.state['error_message'] = error_msg
        self.state['current_stage'] = 'error'
    
    def get_state(self) -> ADMARState:
        """Return current state for agent consumption."""
        return self.state
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Return workflow status summary."""
        return {
            'stage': self.state['current_stage'],
            'quality_score': self.state['quality_score'],
            'validation_passed': self.state['validation_passed'],
            'retry_count': self.state['retry_count'],
            'error': self.state['error_message']
        }
