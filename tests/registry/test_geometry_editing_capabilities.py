from blender_mcp_server.capabilities.geometry import get_capabilities


def _ids():
    return {cap.id for cap in get_capabilities()}


def test_geometry_capabilities_registered():
    ids = _ids()

    expected = {
        "mesh.extrude",
        "mesh.bevel",
        "mesh.inset",
        "mesh.boolean",
        "curve.create",
        "surface.create_nurbs",
    }

    assert expected <= ids


def test_geometry_categories():
    for capability in get_capabilities():
        assert capability.category in {
            "mesh",
            "curve",
            "surface",
        }


def test_geometry_all_modify():
    for capability in get_capabilities():
        assert capability.undo_supported is True
