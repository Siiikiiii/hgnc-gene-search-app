"""
Flask entry point for the HGNC gene search application.

The application factory pattern used here is adapted from the Flask
documentation:
https://flask.palletsprojects.com/en/stable/patterns/appfactories/
"""

from flask import Flask, request, render_template
from pathlib import Path
import logging
from typing import Dict, Any, List, Optional

from hgnc_app import settings
from hgnc_app.models import data_parser
from hgnc_app.logger import setup_logging


# -------------------------------------------------------------------
# Application Factory
# -------------------------------------------------------------------
def create_app() -> Flask:
    """
    Create and configure the Flask application.

    This function encapsulates application creation to avoid
    global side-effects and allow flexible configuration.

    Returns
    -------
    Flask
        Configured Flask application instance.
    """

    # Building the app inside a function keeps set-up (logging, data
    # loading, route registration) in one place that runs when an app is
    # requested, rather than as a side effect scattered across imports.
    # Note that the module-level `app` below still calls this on import.
    app: Flask = Flask(__name__)

    # ---------------------------------------------------------------
    # Logging setup
    # ---------------------------------------------------------------
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Initialising Flask application via factory")

    # ---------------------------------------------------------------
    # Load data
    # ---------------------------------------------------------------
    # The HGNC complete set (~45,000 genes, ~17 MB) is parsed once at
    # start-up rather than per request: re-reading the file for every
    # search would take seconds, whereas searching the in-memory list
    # takes milliseconds. The data is read-only, so sharing one copy
    # between requests is safe.
    DATA_FILE = settings.DATA_FILE

    logger.info(f"Loading data from {DATA_FILE}")

    try:
        # Keep the dataset on the app instance rather than in a module
        # global, so the routes below always read the data that belongs
        # to the app they are registered on.
        app.config["DATA"] = data_parser.read_file(DATA_FILE)
        logger.info("Data loaded successfully")

    except Exception:
        # Fail fast: without the dataset the app cannot answer any query,
        # so refusing to start is clearer than serving errors on every
        # search.
        logger.exception("Failed to load data")
        raise

    # ---------------------------------------------------------------
    # Routes
    # ---------------------------------------------------------------

    @app.route("/")
    def home() -> str:
        """
        Render the homepage.

        Returns
        -------
        str
            Rendered HTML template.
        """
        logger.debug("Rendering homepage")
        return render_template("index.html")

    @app.route("/search", methods=["POST"])
    def search() -> str:
        """
        Handle gene search requests.

        This endpoint retrieves a gene information including previous symbols, aliases,
        and MANE transcripts form input (i.e., an HGNC-approved gene symbol or an HGNC ID)
        and queries the dataset loaded at application creation.

        Returns
        -------
        str
            Rendered template containing results or error messages.
        """
        try:
            query: str = request.form.get("gene", "").strip()
            logger.debug(f"Received search request for gene: {query}")

            # -------------------------------------------------------
            # Validate input
            # -------------------------------------------------------
            if not query:
                logger.warning("No search term provided")
                return render_template(
                    "index.html",
                    error_message="Error: No search term provided. Please enter a gene symbol or HGNC ID.",
                )

            # -------------------------------------------------------
            # Look up the gene in the dataset loaded at start-up
            # -------------------------------------------------------
            data: List[Dict[str, Any]] = app.config["DATA"]

            selection: Optional[Dict[str, Any]] = data_parser.find_gene(query, data)

            if selection is None:
                logger.info(f"Gene not found: {query}")
                return render_template(
                    "index.html",
                    error_message=f"Error: Gene '{query}' not found"
                )

            logger.info(f"Gene found: {query}")

            return render_template("index.html", gene_data=selection)

        # Last-resort handlers: show the user a message on the page
        # instead of Flask's generic 500 error, and record the full
        # traceback in the log for troubleshooting.
        except KeyError as e:
            logger.warning(f"Missing expected data field: {e}")
            return render_template(
                "index.html",
                error_message=f"Error: missing data field {str(e)}"
            )

        except Exception as e:
            logger.exception("Unexpected error during search")
            return render_template(
                "index.html",
                error_message=f"Error: {str(e)}"
            )

    return app

# -------------------------------------------------------------------
# Application instance
# -------------------------------------------------------------------
# WSGI servers (e.g. gunicorn hgnc_app.app:app) and the test suite import
# a ready-made `app`, so one is created at import time. This means
# importing this module loads the full HGNC dataset.
app: Flask = create_app()


# -------------------------------------------------------------------
# Entry point (local development only)
# -------------------------------------------------------------------
if __name__ == "__main__":
    logging.getLogger(__name__).info("Running Flask app")
    app.run()