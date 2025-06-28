# autogen-websocket
autogen agent websocket

通过websocket引入user-agent，实现必要信息前端收集，还有mcp服务的启动，一个简单agent项目

在config.py文件中修改qwen或者自己部署的模型的base_url、model_name、api_key等信息，即可启动

## install
`autogen-agentchat`
`autogen-ext[openai]`
`autogen-ext[mcp]`
`autogen`
`fastmcp`
`fastapi`

#run
``python weather-mcp.py``
``python main.py``
``http://127.0.0.1:8080/``

#使用agent_graph_flow/graph_flow
``修复p->e、p->u、u->e，跳不到u的问题``