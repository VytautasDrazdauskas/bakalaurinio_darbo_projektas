-- LuaRocks configuration

rocks_trees = {
   { name = "user", root = home .. "/.luarocks" };
   { name = "system", root = "/home/vytautas/repo/bakalaurinio_darbo_projektas/device/dev_app" };
}
lua_interpreter = "lua";
variables = {
   LUA_DIR = "/home/vytautas/repo/bakalaurinio_darbo_projektas/device/dev_app";
   LUA_BINDIR = "/home/vytautas/repo/bakalaurinio_darbo_projektas/device/dev_app/bin";
}
