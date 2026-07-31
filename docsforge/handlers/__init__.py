"""docsforge 内置 handler 包。

不在此处主动导入子模块（会与 registry.load_builtin_handlers 的延迟加载冲突）。
子模块通过 @register("name") 在导入时自注册；统一由 registry.load_builtin_handlers()
显式触发。
"""
