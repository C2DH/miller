import os, re
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path  # python3 only
from dotenv import dotenv_values
from typing import Any, Optional

# # e.g. set ENV=production to get .production.env file
dotenv_filename = (
    ".{0}.env".format(os.environ.get("ENV", "")) if "ENV" in os.environ else ".env"
)
dotenv_path = str(Path(".") / dotenv_filename)
dotenv_dict = dotenv_values(dotenv_path=dotenv_path, verbose=True)

print(f"Loading env file: \033[94m{dotenv_path}\033[0m")
# check that the file exists
if not os.path.exists(dotenv_path):
    raise ImproperlyConfigured("No .env file found at {0}".format(dotenv_path))

# for k, v in dotenv_dict.items():
#     print("{0}={1}".format(k, v))


def get_env_variable(var_name: str, default: Optional[Any] = None) -> Any:
    """
    Retrieve the value of an environment variable based on the selected environment file.

    The function first checks if the variable is defined in the dotenv file corresponding to the
    current environment mode, as determined by the `ENV` setting. If `ENV` is set to a specific value
    (e.g., `test`), the function loads variables from `.test.env`. If the variable is not found in
    the dotenv file, it then checks the system's environment variables. If still not found, it returns
    the `default` value if provided, or raises an error if required.

    Environment Modes:
        Set `ENV` to specify which dotenv file to load:
        - `ENV=production` loads `.production.env`.
        - `ENV=test` loads `.test.env`.
        - If `ENV` is not set, the default `.env` file may be used.

    Args:
        var_name (str): Name of the environment variable to retrieve.
        default (Optional[Any]): Value to return if the variable is not found. Defaults to None.

    Returns:
        Any: The value of the environment variable or the `default` value if not found.

    Raises:
        ImproperlyConfigured: If the environment variable is not found and no `default` is provided.

    Example:
        >>> get_env_variable('DATABASE_URL', default='sqlite:///:memory:')
    """
    if var_name in dotenv_dict:
        return dotenv_dict[var_name]
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)
