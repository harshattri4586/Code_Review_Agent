from langgraph.graph import StateGraph, END
from core.state import ReviewState


from core.nodes.idempotency_check import idempotency_check
from core.nodes.fetch_diff import fetch_diff
from core.nodes.fetch_context import fetch_context
from core.nodes.review_files import review_files
from core.nodes.aggregate_results import aggregate_results
from core.nodes.post_review import post_review

def route_after_idempotency(state:  ReviewState) -> str:
    """
    Conditional edge function.
    Returns the name of the next node to run, or END to stop the graph.
    """
    if state.get("is_stale"):
        return END
    
    return "fetch_diff"

def build_graph():
    graph = StateGraph(ReviewState)

    ## register node
    graph.add_node("idempotency_check", idempotency_check)
    graph.add_node("fetch_diff", fetch_diff)
    graph.add_node("fetch_context", fetch_context)
    graph.add_node("review_files", review_files)
    graph.add_node("aggregate_results", aggregate_results)
    graph.add_node("post_review", post_review)

    ## Entry point
    graph.set_entry_point("idempotency_check")

    ## conditional branch
    graph.add_conditional_edges(
        "idempotency_check",
        route_after_idempotency,
        {
            "fetch_diff": "fetch_diff",
            END: END
        },
    )

    ## Fixed Sequential edges 
    graph.add_edge("fetch_diff", "fetch_context")
    graph.add_edge("fetch_context", "review_files")
    graph.add_edge("review_files", "aggregate_results")
    graph.add_edge("aggregate_results", "post_review")
    graph.add_edge("post_review", END)

    return graph.compile()
