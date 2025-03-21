"""Define the state structures for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated
from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
@dataclass
class InputState:
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )
    """
    Messages tracking the primary execution state of the agent.

    Typically accumulates a pattern of:
    1. HumanMessage - user input
    2. AIMessage with .tool_calls - agent picking tool(s) to use to collect information
    3. ToolMessage(s) - the responses (or errors) from the executed tools
    4. AIMessage without .tool_calls - agent responding in unstructured format to the user
    5. HumanMessage - user responds with the next conversational turn

    Steps 2-5 may repeat as needed.

    The `add_messages` annotation ensures that new messages are merged with existing ones,
    updating by ID to maintain an "append-only" state unless a message with the same ID is provided.
    """


@dataclass
class State(InputState):
    """Represents the complete state of the agent, extending InputState with additional attributes.

    This class can be used to store any information needed throughout the agent's lifecycle.
    """

    is_last_step: IsLastStep = field(default=False)
    """
    Indicates whether the current step is the last one before the graph raises an error.

    This is a 'managed' variable, controlled by the state machine rather than user code.
    It is set to 'True' when the step count reaches recursion_limit - 1.
    """

    # Additional attributes can be added here as needed.
    # Common examples include:
    # retrieved_documents: List[Document] = field(default_factory=list)
    # extracted_entities: Dict[str, Any] = field(default_factory=dict)
    # api_connections: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuestionState(TypedDict):
    """Represents the state of the question generation process."""
    text: str
    questions: Dict[str, Any] 
    training_id: str
    topic_id: str
    status: str = "pending"


class TopicsState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)

    #messages: Annotated[list, add_messages]
    topic: str
    question: Optional[str] = None
    status: str  # "start" para explicación, "question" para responder preguntas
    response: Optional[str] = None  # Se llenará con la respuesta generada
    id_user: str
    messages: List[Dict[str, str]]  # Agregamos el historial de mensajes


# Definición de estados para LangGraph
class GenerateTopicsState(TypedDict):
    training_name: str
    description: str
    document_id: str
    url: Optional[str]
    topics_list: List[str]
    topics_json: List[Dict[str, Any]]


class FeedbackState(TypedDict):
    cuestionario: str
    feedback: str
    status: str

