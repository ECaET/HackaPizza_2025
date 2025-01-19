from Chains.graph_qa_chain import get_graph_qa_chain
from Graph.state import GraphState

def prompt_template(state: GraphState):
    
    '''Returns a dictionary of at least one of the GraphState'''
    '''Create a simple prompt tempalate for graph qa chain'''
    
    question = state["question"]

    # Create a prompt template
    prompt = create_few_shot_prompt()
    
    return {"prompt": prompt, "question":question}


def graph_qa(state: GraphState):
    
    ''' Returns a dictionary of at least one of the GraphState '''
    ''' Invoke a Graph QA Chain '''
    
    question = state["question"]
    
    graph_qa_chain = get_graph_qa_chain(state)
    
    result = graph_qa_chain.invoke(
        {
            #"context": graph.schema, 
            "query": question,
        },
    )
    return {"documents": result, "question": question}