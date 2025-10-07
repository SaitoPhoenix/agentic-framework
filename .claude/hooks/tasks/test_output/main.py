import json
import sys
from typing import Dict, Any


def test_output(
    input_data: Dict[str, Any],
    global_config: Dict[str, Any],
    **kwargs,
) -> Dict[str, Any]:
    output = {
        "systemMessage": "This is the test_output system message.",
    }

    return output
