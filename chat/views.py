# chat/views.py
from typing import Any, Dict, List, Union

from asgiref.sync import async_to_sync
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.services.search_service import DocumentSearch, search_documents
from documents.models import Category, Correction

from .forms import DebugForm, DebugVectorForm, SearchForm
from .global_registry import websockets
from .serializers import AsyncSearchSerializer
from ai.tasks import async_search

class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""

    def __init__(self, session_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = session_id

    def on_chat_model_start(self, *args, **kwargs):
        """Run when chat model starts running."""

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        consumer = websockets.get(self.session_id)
        if consumer:
            async_to_sync(consumer.channel_layer.send)(
                consumer.channel_name,
                {
                    "type": "send.token",
                    "token": token,
                },
            )

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when LLM errors."""

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends running."""

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when chain errors."""

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when tool errors."""

    def on_text(self, text: str, **kwargs: Any) -> None:
        """Run on arbitrary text."""

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Run on agent end."""


def search(request, category_slug="documents"):
    """
    This function handles the search request.
    It takes in a request and a category_slug as parameters.

    If the request method is POST, it processes the search query
    and returns the search results in a JsonResponse.
    If the request method is not POST, it renders the search form.

    Parameters:
    request (HttpRequest): The search request.
    category_slug (str): The category to search in. Default is "documents".

    Returns:
    JsonResponse: The search results if the request method is POST.
    HttpResponse: The search form if the request method is not POST.
    """
    if request.method == "POST":
        session_id = request.POST.get("session_id")
        callback = StreamingCallbackHandler(session_id)
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            engine = (
                form.cleaned_data["engine"] or "gpt-3.5-turbo"
            )  # Set the engine value to "gpt-3.5-turbo" if it is null
            results = search_documents(
                query, engine, category_slug, prompt=None, k=None, callback=callback
            )

            category = Category.objects.get(slug=category_slug)
            correction = Correction.objects.filter(
                category_id=category.id, query=query
            ).first()
            correction_id = correction.id if correction is not None else None
            response = {"result": results["result"], "source_documents": []}
            if correction_id is not None:
                response["correction_id"] = correction_id
            return JsonResponse(response)
    else:
        form = SearchForm()

    category = Category.objects.get(slug=category_slug)
    return render(
        request,
        "chat/search.html",
        {"form": form, "category": category, "websocket_host": settings.WEBSOCKET_URL},
    )


def debug(request):
    """
    This function handles the debug request. It takes in a request as a parameter.
    If the request method is POST, it processes the debug query and returns the debug results.
    If the request method is not POST, it renders the debug form.

    Parameters:
    request (HttpRequest): The debug request.

    Returns:
    HttpResponse: The debug form if the request method is not POST.
    """
    category_id = request.GET.get("category")
    results = ""
    if category_id:
        category = Category.objects.get(id=category_id)
        form = DebugForm(instance=category)
    else:
        form = DebugForm()

    if request.method == "POST":
        form = DebugForm(request.POST)
        if form.is_valid():
            engine = form.cleaned_data["engine"]
            category_slug = form.cleaned_data["category"].slug
            prompt = form.cleaned_data["prompt"]
            k = form.cleaned_data["k"]
            query = form.cleaned_data["query"]
            results = search_documents(query, engine, category_slug, prompt, k)

    return render(request, "chat/debug.html", {"form": form, "results": results})


def debug_vector(request):
    """
    This function handles the debug vector request. It takes in a request as a parameter.
    If the request method is POST, it processes the debug vector query
    and returns the debug vector results.
    If the request method is not POST, it renders the debug vector form.

    Parameters:
    request (HttpRequest): The debug vector request.

    Returns:
    HttpResponse: The debug vector form if the request method is not POST.
    """
    category_id = request.GET.get("category")
    documents = []
    if category_id:
        category = Category.objects.get(id=category_id)
        form = DebugVectorForm(instance=category)
    else:
        form = DebugVectorForm()

    if request.method == "POST":
        form = DebugVectorForm(request.POST)
        if form.is_valid():
            k = form.cleaned_data["k"]
            category_id = form.cleaned_data["category"].id
            query = form.cleaned_data["query"]

            category = Category.objects.get(id=category_id)
            document_search = DocumentSearch(category=category)
            documents = document_search.get_relevant_documents(query, k=k)

    return render(
        request, "chat/debug_vector.html", {"form": form, "documents": documents}
    )


class SearchAPIView(APIView):
    """
    This class-based view handles the search API request.
    It takes in a request and a category_slug as parameters.
    If the request method is POST, it processes the search query
    and returns the search results in a JsonResponse.
    If the request method is not POST, it returns the form errors with a 400 status.

    Parameters:
    request (HttpRequest): The search request.
    category_slug (str): The category slug. Default is "documents".

    Returns:
    Response: The search results in a JsonResponse if the request method is POST.
    Response: The form errors with a 400 status if the request method is not POST.
    """

    def post(self, request, category_slug="documents"):
        """
        Handles the POST request for the search API.

        Parameters:
        request (HttpRequest): The search request.
        category_slug (str): The category slug. Default is "documents".

        Returns:
        Response: The search results in a JsonResponse if the form is valid.
        Response: The form errors with a 400 status if the form is not valid.
        """
        form = SearchForm(request.data)
        if form.is_valid():
            query = form.cleaned_data["query"]
            engine = form.cleaned_data["engine"] or "gpt-3.5-turbo"
            results = search_documents(query, engine, category_slug)

            return Response({"result": results["result"], "source_documents": []})

        return Response(form.errors, status=400)


class AsyncSearchView(APIView):
    """
    API endpoint that handles asynchronous search requests.

    This view expects a `callback_url`, `query`, `engine`, and `category_slug` in the POST
    request data. It schedules the search for asynchronous processing and the results are
    sent to the provided `callback_url`.
    """

    # Override throttle_classes for this view
    throttle_classes = []

    def post(self, request, *args, **kwargs):
        """
        Handle a POST request to initiate an asynchronous chat.

        Args:
            request (Request): DRF request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response indicating the chat has been scheduled or errors.
        """

        serializer = AsyncSearchSerializer(data=request.data)

        if serializer.is_valid():
            callback_url = serializer.validated_data["callback_url"]
            query = serializer.validated_data["query"]
            engine = serializer.validated_data["engine"]
            category_slug = serializer.validated_data["category_slug"]

            async_search.delay(
                callback_url=callback_url,
                query=query,
                category_slug=category_slug,
                engine=engine,
            )
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
