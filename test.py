{
  "info": {
    "name": "Agent API Tests",
    "description": "Test collection for the Agent API endpoints",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status code is 200\", function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test(\"Response includes status and version\", function () {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.have.property('status');",
              "    pm.expect(jsonData).to.have.property('version');",
              "    pm.expect(jsonData.status).to.eql('OK');",
              "});"
            ],
            "type": "text/javascript"
          }
        }
      ]
    },
    {
      "name": "List Tools",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/tools",
          "host": ["{{base_url}}"],
          "path": ["tools"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status code is 200\", function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test(\"Response has tools array\", function () {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.have.property('tools');",
              "    pm.expect(jsonData.tools).to.be.an('array');",
              "});",
              "",
              "pm.test(\"Tools have required properties\", function () {",
              "    var jsonData = pm.response.json();",
              "    if (jsonData.tools.length > 0) {",
              "        pm.expect(jsonData.tools[0]).to.have.property('name');",
              "        pm.expect(jsonData.tools[0]).to.have.property('description');",
              "    }",
              "});"
            ],
            "type": "text/javascript"
          }
        }
      ]
    },
    {
      "name": "Add Tool",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"name\": \"test_tool_{{$timestamp}}\",\n    \"description\": \"A test tool created by Postman\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/tools",
          "host": ["{{base_url}}"],
          "path": ["tools"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status code is 200\", function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test(\"Tool added successfully\", function () {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.have.property('message');",
              "    pm.expect(jsonData.message).to.include('added successfully');",
              "});",
              "",
              "// Save the tool name for later tests",
              "var requestBody = JSON.parse(pm.request.body.raw);",
              "pm.collectionVariables.set(\"test_tool_name\", requestBody.name);"
            ],
            "type": "text/javascript"
          }
        }
      ]
    },
    {
      "name": "Update Tool",
      "request": {
        "method": "PUT",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"description\": \"Updated description for test tool\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/tools/{{test_tool_name}}",
          "host": ["{{base_url}}"],
          "path": ["tools", "{{test_tool_name}}"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status code is 200\", function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test(\"Tool updated successfully\", function () {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.have.property('message');",
              "    pm.expect(jsonData.message).to.include('updated successfully');",
              "});"
            ],
            "type": "text/javascript"
          }
        }
      ]
    },
    {
      "name": "Delete Tool",
      "request": {
        "method": "DELETE",
        "header": [],
        "url": {
          "raw": "{{base_url}}/tools/{{test_tool_name}}",
          "host": ["{{base_url}}"],
          "path": ["tools", "{{test_tool_name}}"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status code is 200\", function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test(\"Tool deleted successfully\", function () {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.have.property('message');",
              "    pm.expect(jsonData.message).to.include('deleted successfully');",
              "});"
            ],
            "type": "text/javascript"
          }
        }
      ]
    },
    {
      "name": "Run Inference",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "X-Username",
            "value": "test_user"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"query\": \"What is the capital of France?\",\n    \"history\": \"\",\n    \"temperature\": 0.7,\n    \"system_prompt_extra\": \"Be concise and accurate.\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/infer",
          "host": ["{{base_url}}"],
          "path": ["infer"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status code is 200\", function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test(\"Response has required fields\", function () {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.have.property('reasoning');",
              "    pm.expect(jsonData).to.have.property('answer');",
              "});",
              "",
              "pm.test(\"Answer is non-empty\", function () {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData.answer).to.be.a('string').and.not.empty;",
              "});"
            ],
            "type": "text/javascript"
          }
        }
      ]
    },
    {
      "name": "Get Conversations",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/conversations/test_user",
          "host": ["{{base_url}}"],
          "path": ["conversations", "test_user"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "// This test might fail if no conversations exist yet",
              "pm.test(\"Status code is 200 or 404\", function () {",
              "    pm.expect(pm.response.code).to.be.oneOf([200, 404]);",
              "});",
              "",
              "if (pm.response.code === 200) {",
              "    pm.test(\"Response is an array\", function () {",
              "        var jsonData = pm.response.json();",
              "        pm.expect(jsonData).to.be.an('array');",
              "    });",
              "    ",
              "    pm.test(\"Conversations have correct structure\", function () {",
              "        var jsonData = pm.response.json();",
              "        if (jsonData.length > 0) {",
              "            pm.expect(jsonData[0]).to.have.property('conversation_id');",
              "            pm.expect(jsonData[0]).to.have.property('username');",
              "            pm.expect(jsonData[0]).to.have.property('timestamp');",
              "            pm.expect(jsonData[0]).to.have.property('messages');",
              "        }",
              "    });",
              "} else {",
              "    pm.test(\"404 response is for no conversations\", function () {",
              "        var jsonData = pm.response.json();",
              "        pm.expect(jsonData).to.have.property('detail');",
              "        pm.expect(jsonData.detail).to.include('No conversations found');",
              "    });",
              "}"
            ],
            "type": "text/javascript"
          }
        }
      ]
    },
    {
      "name": "Tool Function",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/tools/function",
          "host": ["{{base_url}}"],
          "path": ["tools", "function"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test(\"Status code is 200\", function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test(\"Response contains expected string\", function () {",
              "    var response = pm.response.text();",
              "    pm.expect(response).to.include('Tool function result');",
              "});"
            ],
            "type": "text/javascript"
          }
        }
      ]
    }
  ],
  "event": [
    {
      "listen": "prerequest",
      "script": {
        "type": "text/javascript",
        "exec": [
          ""
        ]
      }
    },
    {
      "listen": "test",
      "script": {
        "type": "text/javascript",
        "exec": [
          ""
        ]
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "string"
    },
    {
      "key": "test_tool_name",
      "value": ""
    }
  ]
}