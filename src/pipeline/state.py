from typing import TypedDict, Optional, Any

class AgentState(TypedDict):
    
    raw_input: str               
    intent: str                  
    
    
    clean_query: Optional[str]   
    retrieved_context: str       
    
    
    generated_command: str 
    generated_index_command:str      
    explanation: str             
    
    
    approval_status: str         
    
    
    execution_result: Any        
    final_latency: float         