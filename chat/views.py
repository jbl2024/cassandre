# chat/views.py
from typing import Any, Dict, List, Union

from asgiref.sync import async_to_sync
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Category, Correction
from ai.services.search_service import search_documents, DocumentSearch

from .forms import DebugForm, DebugVectorForm, SearchForm
from .global_registry import websockets


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""

    def __init__(self, session_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = session_id

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
        pass

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
    This function handles the search request. It takes in a request and a category_slug as parameters.
    If the request method is POST, it processes the search query and returns the search results in a JsonResponse.
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
            document_search = DocumentSearch(category=category, k=k)
            documents = document_search.get_relevant_documents(query)

    return render(
        request, "chat/debug_vector.html", {"form": form, "documents": documents}
    )


class SearchAPIView(APIView):
    def post(self, request, category_slug="documents"):
        form = SearchForm(request.data)
        if form.is_valid():
            query = form.cleaned_data["query"]
            engine = form.cleaned_data["engine"] or "gpt-3.5-turbo"
            results = search_documents(query, engine, category_slug)

            return Response({"result": results["result"], "source_documents": []})

        return Response(form.errors, status=400)
