"""Kick handling: a dead token must NOT trigger an immediate re-login (it would kick the phone app).
Run: python tests/test_kick.py   (needs `requests`, no Home Assistant)"""
import importlib.util, pathlib, sys, time, types
from unittest import mock

PKG = pathlib.Path(__file__).resolve().parent.parent / "custom_components" / "furbulous"
pkg = types.ModuleType("furb"); pkg.__path__ = [str(PKG)]; sys.modules["furb"] = pkg
for name in ("const", "furbulous_api"):
    spec = importlib.util.spec_from_file_location(f"furb.{name}", PKG / f"{name}.py")
    mod = importlib.util.module_from_spec(spec); sys.modules[f"furb.{name}"] = mod; spec.loader.exec_module(mod)
api_mod, const = sys.modules["furb.furbulous_api"], sys.modules["furb.const"]

api = api_mod.FurbulousCatAPI("a@b.c", "pw", region="us", token="old")
assert api.base_url == const.REGIONS["us"][0] and api.ws_url == const.REGIONS["us"][1]

resp = mock.Mock(status_code=200); resp.json.return_value = {"code": 10403, "message": "无效的 Token"}
with mock.patch.object(api.session, "get", return_value=resp), mock.patch.object(api.session, "post") as login:
    try:
        api.get_devices(); raise AssertionError("expected FurbulousCatKicked")
    except api_mod.FurbulousCatKicked:
        pass
    assert api.token is None
    assert 290 < api.kicked_remaining <= const.KICK_COOLDOWN
    try:
        api.authenticate(); raise AssertionError("login during cooldown")
    except api_mod.FurbulousCatKicked:
        pass
    login.assert_not_called()  # the phone was not kicked back

api.kicked_until = time.time() - 1  # cooldown over -> login allowed again
ok = mock.Mock(status_code=200); ok.json.return_value = {"code": 0, "data": {"token": "new", "identityid": "x"}}
with mock.patch.object(api.session, "post", return_value=ok):
    assert api.authenticate() and api.token == "new"
print("kick handling OK")

props = api_mod.extract_properties({"workstatus": {"value": "5", "time": 1}, "catWeight": {"value": 4200}, "mcuversion": {"value": "1.0.3"}, "x": "-1"})
assert props == {"workstatus": 5, "catWeight": 4200, "mcuversion": "1.0.3", "x": -1}, props
print("property normalization OK")
