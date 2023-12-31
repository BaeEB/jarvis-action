from itertools import groupby, islice, zip_longest
import json
import os
import glob
from fix_commit_message import modify_commit_msg

CONTOUR_LINE = "\n\n----\n"
CODE_BLOCK = "\x60\x60\x60"
CODE_BLOCK_FORMAT = "diff"
GITHUB_ACTOR = os.getenv("GITHUB_ACTOR", None)
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_SERVER_URL = os.getenv("GITHUB_SERVER_URL")
GITHUB_SHA = os.getenv("GITHUB_SHA")

JARVIS_OUTPUT_DIR = os.getenv("JARVIS_OUTPUT_DIR")
JARVIS_WORKSPACE = os.getenv("JARVIS_WORKSPACE")
JARVIS_TARGET= os.getenv("JARVIS_TARGET")


def _open_collapsed_section(description):
    return f"\n\n<details><summary>{description}</summary>\n"


def _close_collapsed_section():
    return f"\n\n</details>\n"

def _read_rule_json():
    output_dir = os.path.join(JARVIS_WORKSPACE, "JARVIS", "workspace", "outputs")
    with open(f"{output_dir}/violated_rules.json", "r") as rules:
        rule_info = json.load(rules)
        rule_info_dict = json.loads(rule_info)
    return rule_info_dict

def _gen_diff_list():
    output_dir = os.path.join(JARVIS_WORKSPACE, "JARVIS", "workspace", "outputs")
    print(f"Output dir: {output_dir}")
    diff_list = glob.glob(f"{output_dir}/*.diff")
    print(diff_list)

    return diff_list


def _gen_file_info():
    body = f"{CONTOUR_LINE}Violated file list:\n"
    project_json_list = glob.glob(f"{JARVIS_WORKSPACE}/JARVIS/workspace{JARVIS_TARGET}/.staticdata/*/project.json")
    print(f"{JARVIS_WORKSPACE}/JARVIS/{JARVIS_TARGET}/.staticdata/*/project.json")
    print(project_json_list)

    source_dict_list = []
    for project_json in project_json_list:
        with open(project_json, "r") as project_json_file:
            rule_info = json.load(project_json_file)
            # rule_info_dict = json.loads(rule_info)
            source_dict_list = rule_info["modules"][0]["sources"]
    

    for source_dict in source_dict_list:
        body += source_dict["originalPath"] + "\n"
    
    return body


def _read_summary():
    output_dir = os.path.join(JARVIS_WORKSPACE, "JARVIS", "workspace", "outputs")
    with open(output_dir + "/summary.txt", "r") as f:
        summary = f.read()

    return summary + CONTOUR_LINE

def _gen_rule_info(rule_info_dict):
    body = f"This issue is generated by Vulcan for commit: {GITHUB_SHA}\n"
    body += _open_collapsed_section("Found violations by STATIC")

    for k, v in rule_info_dict.items():
        body += f"{k}: {v} violated.\n"

    body+=_close_collapsed_section()
    return body


def _gen_patch_info(diff_list):
    output_dir = os.path.join(JARVIS_WORKSPACE, "JARVIS", "workspace", "outputs")

    body = f"{CONTOUR_LINE} Violation fixed by jarvis\n"
    body += _open_collapsed_section("plausible patch diff info")
    for diff in diff_list:
        print("Diff: " + diff)
        with open(diff, "r") as f:
            code = f.read()
        body += f"{CONTOUR_LINE}{CODE_BLOCK} {CODE_BLOCK_FORMAT}\n{code}\n{CODE_BLOCK}\n"

    body += _close_collapsed_section()

    return body


def generate_issue_body():
    '''
    |  Rule info   |
    | ------------ |
    |  File info   |
    | ------------ |
    |  Diff info   |
    | ------------ |
    |  Explanation |
    |              |
    '''
    print(f"[DEBUG] create issue body", flush=True)
    title = "Vulcan"
    summary = _read_summary()
    rule_info_dict = _read_rule_json()
    info = _gen_rule_info(rule_info_dict)
    file_info = _gen_file_info()
    diff_list = _gen_diff_list()

    patch_info = ""
    output_dir = os.path.join(JARVIS_WORKSPACE, "JARVIS", "workspace", "outputs")
    patch_info = _gen_patch_info(diff_list)
    
    explanation = f"{CONTOUR_LINE}{modify_commit_msg(diff_list, rule_info_dict)}"
    body = f"{summary}{info}{file_info}{patch_info}{explanation}"
    with open(os.path.join(output_dir, "issue_body"), "w") as f:
        f.write(body)


generate_issue_body()
