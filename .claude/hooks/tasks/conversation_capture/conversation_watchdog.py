#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "watchdog",
#   "pydantic",
# ]
# ///
"""
Claude Code Transcript Capture - Refactored Version
Watches a Claude Code transcript file (JSONL) and incrementally processes new objects
into simplified conversation files (JSON) - NOW WITH IMPROVED ARCHITECTURE!
"""

import json
import sys
import argparse
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Literal, Annotated
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, field_validator

# Import watchdog components
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Define raw object types to ignore BEFORE Pydantic validation.
# These objects have a different structure and would cause a validation error.
IGNORED_OBJECT_TYPES = {"summary", "file-history-snapshot"}

# Define message types to ignore AFTER Pydantic validation.
# These objects are structurally valid but are not part of the main conversation.
IGNORED_MESSAGE_TYPES = {"system"}

# ==============================================================================
# DOMAIN MODELS
# ==============================================================================


class OperationType(Enum):
    """Types of operations in conversations"""

    RESPONSE = "response"
    THINKING = "thinking"
    TOOL_TASK = "Tool:Task"
    TOOL_READ = "Tool:Read"
    TOOL_WRITE = "Tool:Write"
    TOOL_BASH = "Tool:Bash"
    TOOL_EDIT = "Tool:Edit"
    TOOL_MULTI_EDIT = "Tool:MultiEdit"
    TOOL_WEB_FETCH = "Tool:WebFetch"
    TOOL_WEB_SEARCH = "Tool:WebSearch"
    TOOL_GLOB = "Tool:Glob"
    TOOL_GREP = "Tool:Grep"
    TOOL_MCP = "Tool:MCP"
    TOOL_OTHER = "Tool:Other"


# Define models for the different types of content within a message
class TextContent(BaseModel):
    type: Literal["text"]
    text: str


class ToolUseContent(BaseModel):
    type: Literal["tool_use"]
    id: str
    name: str
    input: Dict[str, Any]


class ToolResultContent(BaseModel):
    type: Literal["tool_result"]
    tool_use_id: str
    # FIX 3: Allow content to be a string OR a list of text blocks.
    content: Union[str, List[TextContent]]
    is_error: bool = False


class ThinkingContent(BaseModel):
    type: Literal["thinking"]
    thinking: str
    signature: Optional[str] = None


# A discriminated union will automatically parse into the correct model
# based on the 'type' field.
ContentItem = Annotated[
    Union[TextContent, ToolUseContent, ToolResultContent, ThinkingContent],
    Field(discriminator="type"),
]


class MessageContent(BaseModel):
    content: List[ContentItem]

    # FIX 2: Add a validator to handle cases where 'content' is a string
    @field_validator("content", mode="before")
    @classmethod
    def convert_str_to_content_list(cls, v: Any) -> Any:
        if isinstance(v, str):
            # If the input is a plain string, wrap it in the expected structure
            return [{"type": "text", "text": v}]
        return v


# This is the top-level model for each line in the JSONL file.
class TranscriptLine(BaseModel):
    uuid: str
    parent_uuid: Optional[str] = Field(None, alias="parentUuid")
    timestamp: str
    is_sidechain: bool = Field(alias="isSidechain")
    message_type: str = Field(alias="type")
    # FIX 1: Make the message field optional to handle metadata lines
    message: Optional[MessageContent] = None
    is_meta: bool = Field(False, alias="isMeta")


@dataclass
class ConversationMessage:
    """Simplified conversation message structure"""

    id: str  # 5-character UUID prefix
    parent_id: Optional[str]  # 5-character UUID prefix
    timestamp: str
    speaker: str
    operation: OperationType
    message: str
    is_sidechain: bool
    chain_id: Optional[str] = None
    order: str = ""

    # Internal processing fields
    _uuid: str = ""
    _original_parent_uuid: Optional[str] = None
    _original_chain_id: Optional[str] = None


# ==============================================================================
# JSON PARSER (REFACTORED FOR EFFICIENCY)
# ==============================================================================


class JSONParser:
    """Handles reading and parsing JSONL files efficiently."""

    def __init__(self):
        self.file_handle = None
        self.last_pos = 0
        self.filepath = ""

    def open_file(self, filepath: str):
        """Opens the transcript file and seeks to the end."""
        try:
            self.filepath = filepath
            # Open in read mode 'r' with UTF-8 encoding
            self.file_handle = open(self.filepath, "r", encoding="utf-8")
            # Go to the end of the file to ignore existing content initially
            self.file_handle.seek(0, 2)
            self.last_pos = self.file_handle.tell()
            print(f"Opened {filepath}, starting at position {self.last_pos}.")
        except FileNotFoundError:
            print(
                f"Input file {filepath} not found yet. Will wait for it to be created.",
                file=sys.stderr,
            )
            self.file_handle = None  # Ensure handle is None if file doesn't exist
        except Exception as e:
            print(f"Error opening file: {e}", file=sys.stderr)
            self.file_handle = None

    def close_file(self):
        """Closes the file handle gracefully."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            print("\nClosed transcript file.")

    def read_new_objects(self) -> List[TranscriptLine]:
        """Read only new lines from the file since the last check."""
        # If the file wasn't open (e.g., didn't exist before), try opening it now.
        if not self.file_handle and os.path.exists(self.filepath):
            self.open_file(self.filepath)

        if not self.file_handle:
            return []

        # Check if the file was truncated (smaller than our last position)
        current_size = os.path.getsize(self.filepath)
        if current_size < self.last_pos:
            print("File truncated. Resetting to beginning.", file=sys.stderr)
            self.last_pos = 0

        # Seek to the last known position
        self.file_handle.seek(self.last_pos)

        # Read all new content from this position
        new_content = self.file_handle.read()

        # Update the last position to the new end of the file
        self.last_pos = self.file_handle.tell()

        if not new_content:
            return []

        json_objects = self._parse_jsonl_content(
            new_content
        )  # This method is unchanged

        # CHANGED: Use Pydantic for parsing and validation
        validated_objects = []
        for obj in json_objects:
            if obj.get("type") in IGNORED_OBJECT_TYPES:
                continue
            try:
                # Pydantic handles all the validation and conversion!
                line_model = TranscriptLine.model_validate(obj)
                validated_objects.append(line_model)
            except ValidationError as e:
                # Pydantic gives detailed, human-readable errors.
                print(f"Skipping object due to validation error: {e}", file=sys.stderr)
                print(f"Invalid object data: {str(obj)[:200]}", file=sys.stderr)

        return validated_objects

    def _parse_jsonl_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse JSONL content into list of dictionaries"""
        json_objects = []

        for line_num, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
                json_objects.append(obj)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON on line {line_num}: {e}", file=sys.stderr)
                print(f"Line content (first 200 chars): {line[:200]}", file=sys.stderr)

        return json_objects


# ==============================================================================
# TOOL PROCESSOR
# ==============================================================================


class ToolHandler(ABC):
    """Abstract base class for tool handlers"""

    @abstractmethod
    def can_handle(self, tool_name: str) -> bool:
        """Check if this handler can process the given tool"""
        pass

    @abstractmethod
    def process(self, tool_input: Dict[str, Any]) -> Tuple[OperationType, str]:
        """Process the tool input and return operation type and message"""
        pass


class TaskToolHandler(ToolHandler):
    """Handler for Task tool operations"""

    def can_handle(self, tool_name: str) -> bool:
        return tool_name == "Task"

    def process(self, tool_input: Dict[str, Any]) -> Tuple[OperationType, str]:
        subagent = tool_input.get("subagent_type", "Agent")
        description = tool_input.get("description", "")
        return (
            OperationType.TOOL_TASK,
            f"Going to chat with Agent({subagent}). Topic: {description}",
        )


class FileToolHandler(ToolHandler):
    """Handler for file-related tools (Read, Write, Edit, MultiEdit)"""

    def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["Read", "Write", "Edit", "MultiEdit"]

    def process(self, tool_input: Dict[str, Any]) -> Tuple[OperationType, str]:
        file_path = tool_input.get("file_path", "")

        if tool_input.get("_tool_name") == "Read":
            return OperationType.TOOL_READ, f"Reading the file at {file_path}"
        elif tool_input.get("_tool_name") == "Write":
            return OperationType.TOOL_WRITE, f"Writing a file at {file_path}"
        elif tool_input.get("_tool_name") == "Edit":
            return OperationType.TOOL_EDIT, f"Editing the file at {file_path}"
        elif tool_input.get("_tool_name") == "MultiEdit":
            return OperationType.TOOL_MULTI_EDIT, f"Editing the file at {file_path}"

        return OperationType.TOOL_OTHER, f"File operation on {file_path}"


class BashToolHandler(ToolHandler):
    """Handler for Bash tool operations"""

    def can_handle(self, tool_name: str) -> bool:
        return tool_name == "Bash"

    def process(self, tool_input: Dict[str, Any]) -> Tuple[OperationType, str]:
        command = tool_input.get("command", "")
        description = tool_input.get("description", "")
        message = f"Running Bash command `{command}`"
        if description:
            message += f". Focus: {description}"
        return OperationType.TOOL_BASH, message


class WebToolHandler(ToolHandler):
    """Handler for web-related tools (WebFetch, WebSearch)"""

    def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["WebFetch", "WebSearch"]

    def process(self, tool_input: Dict[str, Any]) -> Tuple[OperationType, str]:
        if tool_input.get("_tool_name") == "WebFetch":
            url = tool_input.get("url", "")
            return OperationType.TOOL_WEB_FETCH, f"Fetching the URL {url}"
        elif tool_input.get("_tool_name") == "WebSearch":
            query = tool_input.get("query", "")
            return OperationType.TOOL_WEB_SEARCH, f"Searching the web for {query}"

        return OperationType.TOOL_OTHER, "Web operation"


class SearchToolHandler(ToolHandler):
    """Handler for search tools (Glob, Grep)"""

    def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["Glob", "Grep"]

    def process(self, tool_input: Dict[str, Any]) -> Tuple[OperationType, str]:
        if tool_input.get("_tool_name") == "Glob":
            pattern = tool_input.get("pattern", "")
            return OperationType.TOOL_GLOB, f"Searching for files matching {pattern}"
        elif tool_input.get("_tool_name") == "Grep":
            pattern = tool_input.get("pattern", "")
            return OperationType.TOOL_GREP, f"Searching for patterns matching {pattern}"

        return OperationType.TOOL_OTHER, "Search operation"


class MCPToolHandler(ToolHandler):
    """Handler for MCP tools"""

    def can_handle(self, tool_name: str) -> bool:
        return tool_name.startswith("mcp")

    def process(self, tool_input: Dict[str, Any]) -> Tuple[OperationType, str]:
        custom_fields = json.dumps(tool_input)
        tool_name = tool_input.get("_tool_name", "mcp_tool")
        return OperationType.TOOL_MCP, f"Running {tool_name} with {custom_fields}"


class DefaultToolHandler(ToolHandler):
    """Default handler for unknown tools"""

    def can_handle(self, tool_name: str) -> bool:
        return True  # Always can handle as fallback

    def process(self, tool_input: Dict[str, Any]) -> Tuple[OperationType, str]:
        tool_name = tool_input.get("_tool_name", "unknown_tool")
        # Remove internal fields from display
        display_input = {k: v for k, v in tool_input.items() if not k.startswith("_")}
        return (
            OperationType.TOOL_OTHER,
            f"Running {tool_name} with input: {json.dumps(display_input)}",
        )


class ToolProcessor:
    """Processes tool usage with strategy pattern"""

    def __init__(self):
        self.handlers = [
            TaskToolHandler(),
            FileToolHandler(),
            BashToolHandler(),
            WebToolHandler(),
            SearchToolHandler(),
            MCPToolHandler(),
            DefaultToolHandler(),  # Must be last as fallback
        ]
        self.tool_use_mapping: Dict[str, Dict[str, Any]] = {}

    def process_tool_use(
        self, tool_name: str, tool_input: Dict[str, Any], tool_id: str = ""
    ) -> Tuple[OperationType, str]:
        """Process tool use and return operation type and message"""
        # Store tool mapping for later reference
        if tool_id:
            self.tool_use_mapping[tool_id] = {
                "name": tool_name,
                "input": tool_input,
            }

        # Add tool name to input for handlers
        tool_input_with_name = {**tool_input, "_tool_name": tool_name}

        # Find appropriate handler
        for handler in self.handlers:
            if handler.can_handle(tool_name):
                return handler.process(tool_input_with_name)

        # This should never happen due to DefaultToolHandler
        return OperationType.TOOL_OTHER, f"Unknown tool: {tool_name}"


# ==============================================================================
# FILE CHANGE HANDLER
# ==============================================================================


class TranscriptChangeHandler(FileSystemEventHandler):
    """Handles file system events for the transcript file."""

    def __init__(self, capturer, input_filepath: str, output_filepath: str):
        self.capturer = capturer
        self.input_filepath = os.path.abspath(input_filepath)
        self.output_filepath = output_filepath

    def on_modified(self, event):
        """This method is called by watchdog when a file is modified."""
        if (
            not event.is_directory
            and os.path.abspath(event.src_path) == self.input_filepath
        ):
            print(f"Detected change in {self.input_filepath}")
            try:
                self.capturer.process_new_changes(self.output_filepath)
            except Exception as e:
                print(f"Error during processing event: {e}", file=sys.stderr)


# ==============================================================================
# MAIN TRANSCRIPT CAPTURER (REFACTORED FOR INCREMENTAL PROCESSING)
# ==============================================================================


class TranscriptCapturer:
    """Main orchestrator for transcript processing using Pydantic and incremental updates."""

    def __init__(self, human_name: str = "Human", primary_agent: str = "Assistant"):
        self.human_name = human_name
        self.primary_agent = primary_agent

        # Components
        self.json_parser = JSONParser()
        self.tool_processor = ToolProcessor()

        # State
        self.conversations: List[ConversationMessage] = []
        self.all_raw_objects_map: Dict[
            str, TranscriptLine
        ] = {}  # Use TranscriptLine model

        # Relationship tracking
        self.task_to_chain_mapping: Dict[str, str] = {}
        self.chain_to_agent_mapping: Dict[str, str] = {}
        self.tool_errors: Dict[str, bool] = {}

        # State for incremental processing
        self.uuid_to_conv: Dict[str, ConversationMessage] = {}
        self.primary_order_counter = 1
        self.chain_order_counters: Dict[str, int] = {}

        # Session information
        self.session_id: Optional[str] = None

    def start_watching(self, input_filepath: str, output_filepath: str):
        """Watch input file for changes using an event-driven observer."""
        print(f"Starting to watch {input_filepath} for changes...")
        print(f"Output will be written to {output_filepath}")

        # Extract session_id from input filename (without .jsonl extension)
        self.session_id = Path(input_filepath).stem

        Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
        if not Path(output_filepath).exists():
            self._write_initial_output(output_filepath)

        self.json_parser.open_file(input_filepath)

        if self.json_parser.file_handle:
            print("Processing existing content in input file...")
            # Set position to 0 to read the whole file on the first run
            self.json_parser.last_pos = 0
            self.process_new_changes(output_filepath)

        event_handler = TranscriptChangeHandler(self, input_filepath, output_filepath)
        observer = Observer()
        watch_dir = os.path.dirname(os.path.abspath(input_filepath))
        observer.schedule(event_handler, watch_dir, recursive=False)
        print(f"Now watching directory '{watch_dir}' for events...")
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping file watcher...")
        finally:
            self.json_parser.close_file()
            observer.stop()
            observer.join()

    def process_new_changes(self, output_filepath: str):
        """Process new changes detected in the input file incrementally."""
        new_raw_objects = (
            self.json_parser.read_new_objects()
        )  # This now returns List[TranscriptLine]
        if not new_raw_objects:
            return

        print(f"Processing {len(new_raw_objects)} new objects incrementally...")
        for obj in new_raw_objects:
            self.all_raw_objects_map[obj.uuid] = obj

        self._update_relationship_maps(new_raw_objects)

        newly_added_conversations = 0
        for raw_obj in new_raw_objects:
            conv_msg = self._process_raw_object(raw_obj)
            if conv_msg:
                self._process_and_link_new_message(conv_msg)
                self.conversations.append(conv_msg)
                self.uuid_to_conv[conv_msg._uuid] = conv_msg
                newly_added_conversations += 1

        if newly_added_conversations > 0:
            self.conversations.sort(
                key=lambda x: self._parse_order_for_sorting(x.order)
            )
            self._update_output_file(output_filepath)
            print(
                f"Updated {output_filepath} with {newly_added_conversations} new conversations"
            )

    def _update_relationship_maps(self, new_raw_objects: List[TranscriptLine]):
        """Incrementally update relationship maps with new data using Pydantic models."""
        for raw_obj in new_raw_objects:
            if raw_obj.message_type == "assistant":
                for item in raw_obj.message.content:
                    if isinstance(item, ToolUseContent) and item.name == "Task":
                        prompt = item.input.get("prompt", "")
                        subagent = item.input.get("subagent_type", "Agent")
                        self.task_to_chain_mapping[prompt] = raw_obj.uuid
                        self.chain_to_agent_mapping[raw_obj.uuid] = subagent
            elif raw_obj.message_type == "user":
                for item in raw_obj.message.content:
                    if isinstance(item, ToolResultContent) and item.is_error:
                        if raw_obj.parent_uuid:
                            self.tool_errors[raw_obj.parent_uuid] = True

    def _process_and_link_new_message(self, conv_msg: ConversationMessage):
        """Processes a single new message, linking it to the existing state."""
        valid_parent_uuid = self._find_valid_parent_uuid(conv_msg._original_parent_uuid)
        parent_conv = (
            self.uuid_to_conv.get(valid_parent_uuid) if valid_parent_uuid else None
        )

        if conv_msg.is_sidechain:
            if conv_msg._original_chain_id:
                conv_msg.chain_id = conv_msg._original_chain_id
            elif parent_conv and parent_conv.chain_id:
                conv_msg.chain_id = parent_conv.chain_id
            if conv_msg.chain_id and conv_msg.speaker == "Agent":
                conv_msg.speaker = self.chain_to_agent_mapping.get(
                    conv_msg.chain_id, "Agent"
                )

        if not conv_msg.is_sidechain:
            conv_msg.order = str(self.primary_order_counter)
            self.primary_order_counter += 1
        else:
            if conv_msg.chain_id:
                task_conv = self.uuid_to_conv.get(conv_msg.chain_id)
                if task_conv and task_conv.order:
                    base_order = task_conv.order
                    sub_order = self.chain_order_counters.get(conv_msg.chain_id, 1)
                    conv_msg.order = f"{base_order}.{sub_order}"
                    self.chain_order_counters[conv_msg.chain_id] = sub_order + 1
                else:
                    conv_msg.order = f"unknown.{self.primary_order_counter}"
            else:
                conv_msg.order = f"unknown.{self.primary_order_counter}"

        conv_msg.id = conv_msg._uuid[:5] if conv_msg._uuid else "00000"
        if parent_conv:
            parent_uuid_prefix = parent_conv._uuid[:5] if parent_conv._uuid else "00000"
            conv_msg.parent_id = f"{parent_conv.order}-{parent_uuid_prefix}"
        else:
            conv_msg.parent_id = None

    def _find_valid_parent_uuid(self, start_uuid: Optional[str]) -> Optional[str]:
        """Recursively find the closest valid parent that wasn't filtered out."""
        if not start_uuid:
            return None
        if start_uuid in self.uuid_to_conv:
            return start_uuid
        if start_uuid in self.all_raw_objects_map:
            next_parent_uuid = self.all_raw_objects_map[start_uuid].parent_uuid
            return self._find_valid_parent_uuid(next_parent_uuid)
        return None

    def _process_raw_object(
        self, raw_obj: TranscriptLine
    ) -> Optional[ConversationMessage]:
        """Process a single raw object (TranscriptLine) into a conversation message."""
        if (
            raw_obj.message_type in IGNORED_MESSAGE_TYPES
            or not raw_obj.message
            or raw_obj.is_meta
        ):
            return None

        # Simplified filtering using Pydantic models
        if any(isinstance(item, ToolResultContent) for item in raw_obj.message.content):
            return None
        if any(
            isinstance(item, ToolUseContent) and item.name == "TodoWrite"
            for item in raw_obj.message.content
        ):
            return None

        speaker = self._determine_speaker(raw_obj)
        operation, message = self._extract_operation_and_message(raw_obj)

        if raw_obj.uuid in self.tool_errors and message:
            message = f"FAILED: {message}"

        if operation and message:
            return ConversationMessage(
                id="",
                parent_id="",
                timestamp=raw_obj.timestamp,
                speaker=speaker,
                operation=operation,
                message=message,
                is_sidechain=raw_obj.is_sidechain,
                _uuid=raw_obj.uuid,
                _original_parent_uuid=raw_obj.parent_uuid,
                _original_chain_id=self._determine_chain_id(raw_obj),
            )
        return None

    def _determine_speaker(self, raw_obj: TranscriptLine) -> str:
        """Determine the speaker based on rules."""
        if not raw_obj.is_sidechain:
            return (
                self.human_name
                if raw_obj.message_type == "user"
                else self.primary_agent
            )
        else:
            return self.primary_agent if raw_obj.message_type == "user" else "Agent"
        return "System"

    def _determine_chain_id(self, raw_obj: TranscriptLine) -> Optional[str]:
        """Determine the chain_id for a conversation object."""
        # This logic becomes simpler if we assume the first text content is the key
        if raw_obj.is_sidechain and raw_obj.parent_uuid is None:
            for item in raw_obj.message.content:
                if (
                    isinstance(item, TextContent)
                    and item.text in self.task_to_chain_mapping
                ):
                    return self.task_to_chain_mapping[item.text]
        return None

    def _extract_operation_and_message(
        self, raw_obj: TranscriptLine
    ) -> Tuple[OperationType, str]:
        """Extract operation and message from a TranscriptLine object."""
        for item in raw_obj.message.content:
            if isinstance(item, TextContent):
                return OperationType.RESPONSE, item.text
            if isinstance(item, ThinkingContent):
                return OperationType.THINKING, item.thinking
            if isinstance(item, ToolUseContent):
                return self.tool_processor.process_tool_use(
                    item.name, item.input, item.id
                )
        return (
            OperationType.RESPONSE,
            "",
        )  # Fallback for messages with no processable content

    def _write_initial_output(self, output_filepath: str):
        """Write initial empty output file"""
        initial_output = {
            "metadata": [
                ["generated_at", int(time.time())],
                ["message_count", 0],
                ["primary_chain_count", 0],
                ["sidechain_count", 0],
            ],
            "conversations_headers": [
                "id",
                "order",
                "parent_id",
                "timestamp",
                "speaker",
                "operation",
                "message",
            ],
            "conversations_data": [],
        }

        with open(output_filepath, "w") as f:
            self._write_formatted_json(initial_output, f)

    def _parse_order_for_sorting(self, order: str) -> tuple:
        """Parse order string for proper sorting"""
        if not order:
            return (float("inf"),)

        try:
            parts = order.replace("unknown.", "999.").split(".")
            return tuple(int(part) for part in parts)
        except ValueError:
            return (float("inf"),)

    def _write_formatted_json(self, data: Dict[str, Any], file):
        """Write JSON with custom formatting to match the target style"""
        file.write("{\n")

        # Write metadata
        file.write('    "metadata":[\n')
        for i, item in enumerate(data["metadata"]):
            comma = "," if i < len(data["metadata"]) - 1 else ""
            file.write(f"        {json.dumps(item)}{comma}\n")
        file.write("    ],\n")

        # Write conversations_headers
        file.write(
            f'    "conversations_headers":{json.dumps(data["conversations_headers"])},\n'
        )

        # Write conversations_data
        file.write('    "conversations_data":[\n')
        for i, item in enumerate(data["conversations_data"]):
            comma = "," if i < len(data["conversations_data"]) - 1 else ""
            file.write(f"        {json.dumps(item)}{comma}\n")
        file.write("    ]\n")

        file.write("}\n")

    def _update_output_file(self, output_filepath: str):
        """Update the output file with current conversations"""
        output_data = self._format_conversation_output()

        with open(output_filepath, "w") as f:
            self._write_formatted_json(output_data, f)

    def _format_conversation_output(self) -> Dict[str, Any]:
        """Format conversations for JSON output as array of arrays"""
        headers = [
            "id",
            "order",
            "parent_id",
            "timestamp",
            "speaker",
            "operation",
            "message",
        ]
        data = []

        for conv in self.conversations:
            # Convert ISO timestamp to Unix timestamp
            try:
                from datetime import datetime

                dt = datetime.fromisoformat(conv.timestamp.replace("Z", "+00:00"))
                unix_timestamp = int(dt.timestamp())
            except (ValueError, AttributeError) as e:
                print(f"Error parsing timestamp {conv.timestamp}: {e}", file=sys.stderr)
                unix_timestamp = int(time.time())

            # Extract only the 5-character UUID part from parent_id
            parent_id = conv.parent_id
            if parent_id and "-" in parent_id:
                parent_id = parent_id.split("-", 1)[1]

            row = [
                conv.id,
                conv.order,
                parent_id,
                unix_timestamp,
                conv.speaker,
                conv.operation.value,  # Use enum value
                conv.message,
            ]
            data.append(row)

        # Format metadata
        current_unix_time = int(time.time())
        metadata = [
            ["generated_at", current_unix_time],
            ["message_count", len(self.conversations)],
            [
                "primary_chain_count",
                sum(1 for c in self.conversations if not c.is_sidechain),
            ],
            ["sidechain_count", sum(1 for c in self.conversations if c.is_sidechain)],
            ["session_id", self.session_id or "unknown"],
        ]

        return {
            "metadata": metadata,
            "conversations_headers": headers,
            "conversations_data": data,
        }


# ==============================================================================
# MAIN FUNCTION
# ==============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Watch Claude Code transcript files and incrementally convert to conversation format"
    )
    parser.add_argument(
        "input", type=str, help="Input JSONL transcript file path to watch"
    )
    parser.add_argument("output", type=str, help="Output JSON file path")
    parser.add_argument(
        "--human",
        type=str,
        default="Human",
        help="Name for human speaker (default: Human)",
    )
    parser.add_argument(
        "--agent",
        type=str,
        default="Assistant",
        help="Name for primary agent (default: Assistant)",
    )
    parser.add_argument(
        "--test-once",
        action="store_true",
        help="Process the file once and exit (for testing)",
    )

    args = parser.parse_args()

    capturer = TranscriptCapturer(human_name=args.human, primary_agent=args.agent)

    try:
        if args.test_once:
            # --- CHANGED: Logic for single-run processing ---
            # Extract session_id from input filename for test mode
            capturer.session_id = Path(args.input).stem
            capturer._write_initial_output(args.output)
            if Path(args.input).exists():
                # Open, process all content, then close.
                capturer.json_parser.open_file(args.input)
                # In test mode, we want to read the whole file, so we reset the position
                capturer.json_parser.last_pos = 0
                capturer.process_new_changes(args.output)
                capturer.json_parser.close_file()
                print(f"Processed file and wrote to {args.output}")
            else:
                print(f"Input file {args.input} does not exist", file=sys.stderr)
        else:
            capturer.start_watching(args.input, args.output)
    except Exception as e:
        print(f"Error during capture: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
