"""SF CLI cmdt command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFCmdtOperations(SFBaseOperations):
    """Wraps ``sf cmdt generate`` commands for custom metadata type authoring.

    Most commands generate local metadata files and do not require an org
    connection, so ``include_target_org=False`` is set by default. Only
    :meth:`generate_fromorg` connects to the org to read source object data.
    """

    def generate_field(
        self,
        name: str,
        field_type: str,
        label: str | None = None,
        picklist_values: list[str] | None = None,
        decimal_places: int | None = None,
        output_directory: Path | None = None,
    ) -> dict[str, Any]:
        """Generate a field metadata file for a custom metadata type.

        Args:
            name: Unique API name for the field.
            field_type: Field type. One of: ``Checkbox``, ``Date``,
                ``DateTime``, ``Email``, ``Number``, ``Percent``, ``Phone``,
                ``Picklist``, ``Text``, ``TextArea``, ``LongTextArea``,
                ``Url``.
            label: Human-readable label for the field.
            picklist_values: Picklist values; required when ``field_type``
                is ``Picklist``.
            decimal_places: Decimal places for ``Number`` or ``Percent``
                fields. Defaults to 0.
            output_directory: Directory containing the ``__mdt`` object
                folder where the ``fields/`` subdirectory will be created,
                e.g. ``force-app/main/default/objects/MyCmdt__mdt``.

        Returns:
            Generation result dict.
        """
        args = ["cmdt", "generate", "field", "--name", name, "--type", field_type]

        if label:
            args += ["--label", label]

        if picklist_values:
            for value in picklist_values:
                args += ["--picklist-values", value]

        if decimal_places is not None:
            args += ["--decimal-places", str(decimal_places)]

        if output_directory:
            args += ["--output-directory", str(output_directory)]

        return self._run_capturing(
            args,
            label=f"Generating cmdt field {name}",
            include_target_org=False,
        )

    def generate_object(
        self,
        type_name: str,
        label: str | None = None,
        plural_label: str | None = None,
        visibility: str = "Public",
        output_directory: Path | None = None,
    ) -> dict[str, Any]:
        """Generate a new custom metadata type in the current project.

        Args:
            type_name: Unique API name for the custom metadata type (without
                ``__mdt`` suffix).
            label: Human-readable label.
            plural_label: Plural label; defaults to ``label`` when omitted.
            visibility: Access level: ``Public``, ``Protected``, or
                ``PackageProtected``.
            output_directory: Directory to write the metadata files into
                (e.g. ``force-app/main/default/objects``).

        Returns:
            Generation result dict.
        """
        args = [
            "cmdt",
            "generate",
            "object",
            "--type-name",
            type_name,
            "--visibility",
            visibility,
        ]

        if label:
            args += ["--label", label]

        if plural_label:
            args += ["--plural-label", plural_label]

        if output_directory:
            args += ["--output-directory", str(output_directory)]

        return self._run_capturing(
            args,
            label=f"Generating cmdt object {type_name}",
            include_target_org=False,
        )

    def generate_fromorg(
        self,
        dev_name: str,
        sobject: str,
        label: str | None = None,
        plural_label: str | None = None,
        visibility: str = "Public",
        ignore_unsupported: bool = False,
        type_output_directory: Path | None = None,
        records_output_dir: Path | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Generate a custom metadata type and all its records from a Salesforce object.

        Reads the source object schema and data from the target org, then
        writes the corresponding metadata files locally.

        Args:
            dev_name: Developer name for the new custom metadata type.
            sobject: API name of the source Salesforce object or custom setting.
            label: Human-readable label for the type.
            plural_label: Plural label; defaults to ``label`` when omitted.
            visibility: Access level: ``Public``, ``Protected``, or
                ``PackageProtected``.
            ignore_unsupported: Ignore unsupported field types instead of
                converting them to ``Text``.
            type_output_directory: Directory for the generated type metadata
                files (default ``force-app/main/default/objects``).
            records_output_dir: Directory for the generated record metadata
                files (default ``force-app/main/default/customMetadata``).
            timeout: Subprocess timeout in seconds.

        Returns:
            Generation result dict.
        """
        args = [
            "cmdt",
            "generate",
            "fromorg",
            "--dev-name",
            dev_name,
            "--sobject",
            sobject,
            "--visibility",
            visibility,
        ]

        if label:
            args += ["--label", label]

        if plural_label:
            args += ["--plural-label", plural_label]

        if ignore_unsupported:
            args.append("--ignore-unsupported")

        if type_output_directory:
            args += ["--type-output-directory", str(type_output_directory)]

        if records_output_dir:
            args += ["--records-output-dir", str(records_output_dir)]

        return self._run_capturing(
            args,
            label=f"Generating cmdt {dev_name} from org object {sobject}",
            timeout=timeout,
        )

    def generate_record(
        self,
        type_name: str,
        record_name: str,
        field_values: dict[str, str] | None = None,
        label: str | None = None,
        protected: bool = False,
        input_directory: Path | None = None,
        output_directory: Path | None = None,
    ) -> dict[str, Any]:
        """Generate a single custom metadata type record.

        Args:
            type_name: API name of the custom metadata type (must end in
                ``__mdt``).
            record_name: Name of the new record.
            field_values: Field values as a ``{"FieldName": "value"}`` dict;
                passed as positional ``FieldName=value`` arguments.
            label: Human-readable label for the record.
            protected: Protect the record when in a managed package.
            input_directory: Directory containing the type definition
                (default ``force-app/main/default/objects``).
            output_directory: Directory for the generated record file
                (default ``force-app/main/default/customMetadata``).

        Returns:
            Generation result dict.
        """
        args = [
            "cmdt",
            "generate",
            "record",
            "--type-name",
            type_name,
            "--record-name",
            record_name,
        ]

        if label:
            args += ["--label", label]

        if protected:
            args += ["--protected", "true"]

        if input_directory:
            args += ["--input-directory", str(input_directory)]

        if output_directory:
            args += ["--output-directory", str(output_directory)]

        # Field values are positional arguments in Key=Value format
        if field_values:
            for field, value in field_values.items():
                args.append(f"{field}={value}")

        return self._run_capturing(
            args,
            label=f"Generating cmdt record {type_name}.{record_name}",
            include_target_org=False,
        )

    def generate_records(
        self,
        csv_file: Path,
        type_name: str,
        input_directory: Path | None = None,
        output_directory: Path | None = None,
        name_column: str | None = None,
    ) -> dict[str, Any]:
        """Generate custom metadata type records from a CSV file.

        Args:
            csv_file: Path to the CSV file containing record data.
            type_name: API name of the custom metadata type (``__mdt`` suffix
                is appended automatically if omitted).
            input_directory: Directory containing the type definition
                (default ``force-app/main/default/objects``).
            output_directory: Directory for the generated record files
                (default ``force-app/main/default/customMetadata``).
            name_column: CSV column used to determine each record's name
                (default ``Name``).

        Returns:
            Generation result dict.
        """
        args = [
            "cmdt",
            "generate",
            "records",
            "--csv",
            str(csv_file),
            "--type-name",
            type_name,
        ]

        if input_directory:
            args += ["--input-directory", str(input_directory)]

        if output_directory:
            args += ["--output-directory", str(output_directory)]

        if name_column:
            args += ["--name-column", name_column]

        return self._run_capturing(
            args,
            label=f"Generating cmdt records for {type_name} from {csv_file.name}",
            include_target_org=False,
        )
