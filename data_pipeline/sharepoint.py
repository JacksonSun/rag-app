from office365.sharepoint.client_context import ClientContext

import yaml


def sharepoint_info(file_path):
    with open("/app/credential.yml", "r") as f:
        conn_config = yaml.safe_load(f)
    url = "https://liteon.sharepoint.com/sites/RDExpert"
    ctx = ClientContext(url).with_client_certificate(**conn_config["cert_settings"])
    file_metadata = (
        ctx.web.get_file_by_server_relative_path(file_path)
        .expand(["versions", "listItemAllFields"])
        .get()
        .execute_query()
    )
    uid = file_metadata.unique_id
    return uid
