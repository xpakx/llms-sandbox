import argparse

def get_parser():
    parser = argparse.ArgumentParser(description="A program to manage albums.")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    parser_url = subparsers.add_parser("url", help="Manage URLs")
    url_subparsers = parser_url.add_subparsers(dest="subcommand", help="Available subcommands")
    parser_url_add = url_subparsers.add_parser("add", help="Add a new URL to track")
    parser_url_add.add_argument("url", type=str, help="The URL to add")

    parser_check = subparsers.add_parser("check", help="Check all URLs in the database for new albums")
    parser_view = subparsers.add_parser("view", help="Print all albums in the database")
    return parser
