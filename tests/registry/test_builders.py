from blender_mcp_server.registry import (
    OperationType,
    SecurityLevel,
)
from blender_mcp_server.registry.builders import (
    DEFAULT_MINIMUM_BLENDER_VERSION,
    administrative_capability,
    execution_capability,
    filesystem_capability,
    modify_capability,
    read_capability,
)


def test_read_capability_defaults() -> None:
    capability = read_capability(
        id="scene.inspect",
        category="scene",
        description="Inspect the current scene.",
        result_schema="SceneInfoResult",
    )

    assert capability.operation_type is OperationType.READ
    assert capability.security_level is SecurityLevel.STANDARD
    assert capability.undo_supported is False
    assert capability.async_supported is False
    assert (
        capability.minimum_blender_version
        == DEFAULT_MINIMUM_BLENDER_VERSION
    )
    assert capability.result_schema == "SceneInfoResult"


def test_modify_capability_defaults() -> None:
    capability = modify_capability(
        id="object.translate",
        category="object",
        description="Translate an object.",
        input_schema="ObjectTranslateParams",
        result_schema="ObjectTransformResult",
    )

    assert capability.operation_type is OperationType.MODIFY
    assert capability.security_level is SecurityLevel.STANDARD
    assert capability.undo_supported is True
    assert capability.async_supported is False
    assert capability.input_schema == "ObjectTranslateParams"
    assert capability.result_schema == "ObjectTransformResult"


def test_execution_capability_defaults() -> None:
    capability = execution_capability(
        id="python.execute",
        category="python",
        description="Execute approved Python code.",
        input_schema="PythonExecuteParams",
        result_schema="PythonExecuteResult",
    )

    assert capability.operation_type is OperationType.EXECUTION
    assert capability.security_level is SecurityLevel.RESTRICTED
    assert capability.undo_supported is False
    assert capability.async_supported is False


def test_filesystem_capability_defaults() -> None:
    capability = filesystem_capability(
        id="export.gltf",
        category="export",
        description="Export a Blender scene as glTF.",
        input_schema="ExportGltfParams",
        result_schema="ExportResult",
    )

    assert capability.operation_type is OperationType.FILESYSTEM
    assert capability.security_level is SecurityLevel.RESTRICTED
    assert capability.undo_supported is False


def test_administrative_capability_defaults() -> None:
    capability = administrative_capability(
        id="job.cancel",
        category="job",
        description="Cancel a background job.",
        input_schema="JobIdParams",
        result_schema="JobStatusResult",
    )

    assert capability.operation_type is OperationType.ADMINISTRATIVE
    assert capability.security_level is SecurityLevel.PRIVILEGED
    assert capability.undo_supported is False


def test_builder_allows_overriding_common_metadata() -> None:
    capability = modify_capability(
        id="simulation.bake",
        category="simulation",
        description="Bake a simulation.",
        security_level=SecurityLevel.RESTRICTED,
        undo_supported=False,
        async_supported=True,
        minimum_blender_version="4.0",
        maximum_blender_version="5.2",
        enabled=False,
        deprecated=True,
        input_schema="SimulationBakeParams",
        result_schema="JobResult",
    )

    assert capability.security_level is SecurityLevel.RESTRICTED
    assert capability.undo_supported is False
    assert capability.async_supported is True
    assert capability.minimum_blender_version == "4.0"
    assert capability.maximum_blender_version == "5.2"
    assert capability.enabled is False
    assert capability.deprecated is True


def test_read_capability_preserves_identity_and_description() -> None:
    capability = read_capability(
        id="material.list",
        category="material",
        description="List all materials in the Blender file.",
    )

    assert capability.id == "material.list"
    assert capability.category == "material"
    assert capability.description == (
        "List all materials in the Blender file."
    )


def test_modify_capability_can_disable_undo() -> None:
    capability = modify_capability(
        id="object.external_change",
        category="object",
        description="Perform a non-undoable external change.",
        undo_supported=False,
    )

    assert capability.operation_type is OperationType.MODIFY
    assert capability.undo_supported is False


def test_execution_capability_can_be_async() -> None:
    capability = execution_capability(
        id="render.animation",
        category="render",
        description="Render an animation.",
        async_supported=True,
    )

    assert capability.async_supported is True


def test_filesystem_capability_can_use_standard_security() -> None:
    capability = filesystem_capability(
        id="asset.inspect",
        category="asset",
        description="Inspect an approved asset file.",
        security_level=SecurityLevel.STANDARD,
    )

    assert capability.security_level is SecurityLevel.STANDARD
