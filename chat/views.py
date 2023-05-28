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
from documents.search import search_documents
from documents.search_debug import search_documents_debug

from .forms import DebugForm, SearchForm
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


def document_to_dict(document):
    return {
        "page_content": document.page_content,
        "metadata": document.metadata,
    }


def search(request, category="documents"):
    if request.method == "POST":
        session_id = request.POST.get("session_id")
        callback = StreamingCallbackHandler(session_id)
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            engine = (
                form.cleaned_data["engine"] or "gpt-3.5-turbo"
            )  # Set the engine value to "gpt-3.5-turbo" if it is null
            history = form.cleaned_data["history"] or ""
            results = search_documents(query, history, engine, category, callback)

            category = Category.objects.get(slug=category)
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

    category = Category.objects.get(slug=category)
    return render(
        request,
        "chat/search.html",
        {"form": form, "category": category, "websocket_host": settings.WEBSOCKET_URL},
    )


def debug(request):
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
            category_id = form.cleaned_data["category"].id
            prompt = form.cleaned_data["prompt"]
            k = form.cleaned_data["k"]
            query = form.cleaned_data["query"]
            raw_input = form.cleaned_data["raw_input"]
            results = search_documents_debug(
                engine, category_id, prompt, k, query, raw_input
            )

    return render(request, "chat/debug.html", {"form": form, "results": results})


class SearchAPIView(APIView):
    def post(self, request, category="documents"):
        form = SearchForm(request.data)
        if form.is_valid():
            query = form.cleaned_data["query"]
            engine = form.cleaned_data["engine"] or "gpt-3.5-turbo"
            history = form.cleaned_data["history"] or ""
            results = search_documents(query, history, engine, category)

            return Response({"result": results["result"], "source_documents": []})

        return Response(form.errors, status=400)
