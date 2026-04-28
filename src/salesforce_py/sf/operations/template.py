"""SF CLI template command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


class SFTemplateOperations(SFBaseOperations):
    """Wraps ``sf template generate`` commands for local scaffold generation.

    All commands generate local metadata source files without connecting to an
    org (except :meth:`generate_digital_experience_site`, which accepts an
    optional target org).  ``include_target_org=False`` is set throughout
    except where noted.
    """

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def generate_analytics_template(
        self,
        name: str,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata files for a simple Analytics template.

        Args:
            name: Name of the Analytics template.
            output_dir: Directory to save the generated files (defaults to
                ``waveTemplates`` or the current directory).

        Returns:
            Generation result dict.
        """
        args: list[str] = [
            "template",
            "generate",
            "analytics",
            "template",
            "--name",
            name,
        ]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Analytics template '{name}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # Apex
    # ------------------------------------------------------------------

    def generate_apex_class(
        self,
        name: str,
        template: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for an Apex class.

        Args:
            name: Name of the Apex class (up to 40 characters, must start
                with a letter).
            template: Template to use — one of ``ApexException``,
                ``ApexUnitTest``, ``BasicUnitTest``, ``DefaultApexClass``,
                ``InboundEmailService`` (default: ``DefaultApexClass``).
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = ["template", "generate", "apex", "class", "--name", name]
        if template is not None:
            args += ["--template", template]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Apex class '{name}'",
            include_target_org=False,
        )

    def generate_apex_trigger(
        self,
        name: str,
        template: str | None = None,
        sobject: str | None = None,
        event: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for an Apex trigger.

        Args:
            name: Name of the Apex trigger (up to 40 characters, must start
                with a letter).
            template: Template to use (only permissible value:
                ``ApexTrigger``).
            sobject: Salesforce object the trigger fires on (default
                placeholder ``SOBJECT``).
            event: Comma-separated trigger events, e.g.
                ``"before insert,after insert"`` (default:
                ``"before insert"``).
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = ["template", "generate", "apex", "trigger", "--name", name]
        if template is not None:
            args += ["--template", template]
        if sobject is not None:
            args += ["--sobject", sobject]
        if event is not None:
            args += ["--event", event]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Apex trigger '{name}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # Digital Experience
    # ------------------------------------------------------------------

    def generate_digital_experience_site(
        self,
        name: str,
        template_name: str,
        url_path_prefix: str | None = None,
        admin_email: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for an Experience Cloud site.

        Generates local metadata only (DigitalExperienceConfig,
        DigitalExperienceBundle, Network, CustomSite).  Unlike ``sf community
        create``, this command does not deploy to an org.

        The target org is passed when set on the :class:`SFOrg` instance;
        leave it unset to generate without org context.

        Args:
            name: Name of the Experience Cloud site.
            template_name: Template name, e.g. ``"Build Your Own (LWR)"``.
            url_path_prefix: URL path prefix (alphanumeric only).
            admin_email: Email for the site administrator.
            output_dir: Directory to generate the site files into.

        Returns:
            Generation result dict.
        """
        args: list[str] = [
            "template",
            "generate",
            "digital-experience",
            "site",
            "--name",
            name,
            "--template-name",
            template_name,
        ]
        if url_path_prefix is not None:
            args += ["--url-path-prefix", url_path_prefix]
        if admin_email is not None:
            args += ["--admin-email", admin_email]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating digital experience site '{name}'",
            include_target_org=True,
            include_api_version=False,
        )

    # ------------------------------------------------------------------
    # FlexiPage
    # ------------------------------------------------------------------

    def generate_flexipage(
        self,
        name: str,
        template: str,
        sobject: str | None = None,
        label: str | None = None,
        description: str | None = None,
        primary_field: str | None = None,
        secondary_fields: str | None = None,
        detail_fields: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a FlexiPage (Lightning page).

        Args:
            name: Name of the FlexiPage (alphanumeric, start with a letter,
                no trailing underscore or consecutive underscores).
            template: Page type — one of ``RecordPage``, ``AppPage``,
                ``HomePage``.
            sobject: API name of the SObject; required when
                ``template="RecordPage"``.
            label: Label for the FlexiPage (defaults to the name).
            description: Description of the FlexiPage.
            primary_field: Primary field for RecordPage dynamic highlights
                header (typically ``Name``).
            secondary_fields: Comma-separated secondary fields for the
                dynamic highlights header (max 11 fields); RecordPage only.
            detail_fields: Comma-separated fields for the Details tab;
                RecordPage only.
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = [
            "template",
            "generate",
            "flexipage",
            "--name",
            name,
            "--template",
            template,
        ]
        if sobject is not None:
            args += ["--sobject", sobject]
        if label is not None:
            args += ["--label", label]
        if description is not None:
            args += ["--description", description]
        if primary_field is not None:
            args += ["--primary-field", primary_field]
        if secondary_fields is not None:
            args += ["--secondary-fields", secondary_fields]
        if detail_fields is not None:
            args += ["--detail-fields", detail_fields]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating FlexiPage '{name}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # Lightning (Aura / LWC)
    # ------------------------------------------------------------------

    def generate_lightning_app(
        self,
        name: str,
        template: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a Lightning App bundle.

        Args:
            name: Name of the Lightning App (up to 40 characters, must start
                with a letter).
            template: Template to use (only permissible value:
                ``DefaultLightningApp``).
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = ["template", "generate", "lightning", "app", "--name", name]
        if template is not None:
            args += ["--template", template]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Lightning app '{name}'",
            include_target_org=False,
        )

    def generate_lightning_component(
        self,
        name: str,
        template: str | None = None,
        component_type: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate a bundle for an Aura component or Lightning web component.

        Args:
            name: Name of the component (up to 40 characters, must start with
                a letter).
            template: Template — one of ``default``, ``analyticsDashboard``,
                ``analyticsDashboardWithStep``, ``typescript``.
            component_type: Component type — ``aura`` (default) or ``lwc``.
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = [
            "template",
            "generate",
            "lightning",
            "component",
            "--name",
            name,
        ]
        if template is not None:
            args += ["--template", template]
        if component_type is not None:
            args += ["--type", component_type]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Lightning component '{name}'",
            include_target_org=False,
        )

    def generate_lightning_event(
        self,
        name: str,
        template: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a Lightning Event bundle.

        Args:
            name: Name of the Lightning Event (up to 40 characters, must
                start with a letter).
            template: Template to use (only permissible value:
                ``DefaultLightningEvt``).
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = ["template", "generate", "lightning", "event", "--name", name]
        if template is not None:
            args += ["--template", template]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Lightning event '{name}'",
            include_target_org=False,
        )

    def generate_lightning_interface(
        self,
        name: str,
        template: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a Lightning Interface bundle.

        Args:
            name: Name of the Lightning Interface (up to 40 characters, must
                start with a letter).
            template: Template to use (only permissible value:
                ``DefaultLightningIntf``).
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = [
            "template",
            "generate",
            "lightning",
            "interface",
            "--name",
            name,
        ]
        if template is not None:
            args += ["--template", template]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Lightning interface '{name}'",
            include_target_org=False,
        )

    def generate_lightning_test(
        self,
        name: str,
        template: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a Lightning test.

        Args:
            name: Name of the Lightning test (up to 40 characters, must start
                with a letter).
            template: Template to use (only permissible value:
                ``DefaultLightningTest``).
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = ["template", "generate", "lightning", "test", "--name", name]
        if template is not None:
            args += ["--template", template]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Lightning test '{name}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # Project
    # ------------------------------------------------------------------

    def generate_project(
        self,
        name: str,
        template: str | None = None,
        output_dir: str | Path | None = None,
        namespace: str | None = None,
        default_package_dir: str | None = None,
        manifest: bool = False,
        lwc_language: str | None = None,
    ) -> dict[str, Any]:
        """Generate a Salesforce DX project.

        Args:
            name: Name of the project (also sets ``"name"`` in
                ``sfdx-project.json``).
            template: Project template — one of ``standard``, ``empty``,
                ``analytics``, ``reactinternalapp``, ``reactexternalapp``,
                ``agent`` (default: ``standard``).
            output_dir: Directory to generate the project into.
            namespace: Namespace associated with this project and connected
                scratch orgs.
            default_package_dir: Default package directory name (default:
                ``force-app``).
            manifest: Generate a default ``package.xml`` manifest file.
            lwc_language: LWC language — ``javascript`` or ``typescript``.

        Returns:
            Generation result dict.
        """
        args: list[str] = ["template", "generate", "project", "--name", name]
        if template is not None:
            args += ["--template", template]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        if namespace is not None:
            args += ["--namespace", namespace]
        if default_package_dir is not None:
            args += ["--default-package-dir", default_package_dir]
        if manifest:
            args.append("--manifest")
        if lwc_language is not None:
            args += ["--lwc-language", lwc_language]
        return self._run_capturing(
            args,
            label=f"Generating project '{name}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # Static Resource
    # ------------------------------------------------------------------

    def generate_static_resource(
        self,
        name: str,
        content_type: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a static resource.

        Args:
            name: Name of the static resource (alphanumeric + underscores,
                must start with a letter, no spaces, no trailing underscore,
                no consecutive underscores).
            content_type: MIME type of the resource (default:
                ``application/zip``), e.g. ``application/json``,
                ``text/plain``.
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = ["template", "generate", "static-resource", "--name", name]
        if content_type is not None:
            args += ["--type", content_type]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating static resource '{name}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # UI Bundle
    # ------------------------------------------------------------------

    def generate_ui_bundle(
        self,
        name: str,
        template: str | None = None,
        label: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a UI bundle.

        UI bundles host non-native Salesforce UI frameworks (e.g. React) as
        first-class Salesforce Platform apps.

        Args:
            name: API name of the UI bundle (alphanumeric + underscores,
                must start with a letter).
            template: Template — ``default`` or ``reactbasic``.
            label: Master label for the bundle (defaults to the name).
            output_dir: Output directory.  The CLI automatically appends
                ``uiBundles`` to the path if not already present; the bundle
                is created at ``<output-dir>/uiBundles/<name>``.

        Returns:
            Generation result dict.
        """
        args: list[str] = ["template", "generate", "ui-bundle", "--name", name]
        if template is not None:
            args += ["--template", template]
        if label is not None:
            args += ["--label", label]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating UI bundle '{name}'",
            include_target_org=False,
        )

    # ------------------------------------------------------------------
    # Visualforce
    # ------------------------------------------------------------------

    def generate_visualforce_component(
        self,
        name: str,
        label: str,
        template: str | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a Visualforce component.

        Args:
            name: Name of the Visualforce component (up to 40 characters,
                must start with a letter).
            label: Label for the component (required).
            template: Template to use (only permissible value:
                ``DefaultVFComponent``).
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = [
            "template",
            "generate",
            "visualforce",
            "component",
            "--name",
            name,
            "--label",
            label,
        ]
        if template is not None:
            args += ["--template", template]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Visualforce component '{name}'",
            include_target_org=False,
        )

    def generate_visualforce_page(
        self,
        name: str,
        label: str,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        """Generate metadata source files for a Visualforce page.

        Args:
            name: Name of the Visualforce page (up to 40 characters, must
                start with a letter).
            label: Label for the page (required).
            output_dir: Directory for the generated files.

        Returns:
            Generation result dict.
        """
        args: list[str] = [
            "template",
            "generate",
            "visualforce",
            "page",
            "--name",
            name,
            "--label",
            label,
        ]
        if output_dir is not None:
            args += ["--output-dir", str(output_dir)]
        return self._run_capturing(
            args,
            label=f"Generating Visualforce page '{name}'",
            include_target_org=False,
        )
