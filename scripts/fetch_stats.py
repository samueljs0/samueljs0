"""Busca estatísticas reais do GitHub (via `gh api`) para os cards de stats/tecnologias.
Usa o mesmo token autenticado (`gh auth login`) já usado por fetch_contributions.py,
então não depende de nenhum serviço externo (github-readme-stats etc)."""
import json
import subprocess
from pathlib import Path

USERNAME = "samueljs0"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def gh_json(*args: str) -> object:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def search_total(query: str) -> int:
    proc = subprocess.run(
        ["gh", "api", f"search/{query}&per_page=1", "--jq", ".total_count"],
        capture_output=True, text=True, check=True,
    )
    return int(proc.stdout.strip())


def fetch_repos_and_contributions() -> dict:
    # `owned`: só repos do próprio usuário (público + privado) -> usado para estrelas.
    # `all`: também inclui repos privados/públicos onde ele é colaborador ou membro de
    # organização (ex: projetos de trabalho/faculdade) -> usado para linguagens e contagem
    # de repositórios privados em que participou, não só os que ele é dono.
    query = """
    query($login: String!) {
      user(login: $login) {
        name
        owned: repositories(first: 100, affiliations: [OWNER], isFork: false) {
          nodes { stargazerCount isPrivate }
        }
        all: repositories(first: 100, affiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER], isFork: false) {
          totalCount
          nodes {
            name
            isPrivate
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name color } }
            }
          }
        }
        contributionsCollection {
          totalRepositoriesWithContributedCommits
        }
      }
    }
    """
    return gh_json("api", "graphql", "-f", f"query={query}", "-f", f"login={USERNAME}")


def main() -> None:
    gql = fetch_repos_and_contributions()
    user = gql["data"]["user"]
    owned_repos = user["owned"]["nodes"]
    all_repos = user["all"]["nodes"]

    total_stars = sum(r["stargazerCount"] for r in owned_repos)
    private_repos = sum(1 for r in all_repos if r["isPrivate"])
    contributed_repos = user["contributionsCollection"]["totalRepositoriesWithContributedCommits"]

    lang_bytes: dict[str, dict] = {}
    for repo in all_repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            entry = lang_bytes.setdefault(name, {"size": 0, "color": edge["node"]["color"] or "#8b949e"})
            entry["size"] += edge["size"]

    total_bytes = sum(v["size"] for v in lang_bytes.values()) or 1
    languages = sorted(
        (
            {"name": name, "color": v["color"], "pct": round(v["size"] / total_bytes * 100, 2)}
            for name, v in lang_bytes.items()
        ),
        key=lambda x: x["pct"],
        reverse=True,
    )

    stats = {
        "name": (user.get("name") or USERNAME).title(),
        "stars": total_stars,
        "commits": search_total(f"commits?q=author:{USERNAME}"),
        "prs": search_total(f"issues?q=author:{USERNAME}+type:pr"),
        "issues": search_total(f"issues?q=author:{USERNAME}+type:issue"),
        "contributed_repos": contributed_repos,
        "private_repos": private_repos,
        "languages": languages,
    }

    out_path = DATA_DIR / "stats.json"
    out_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[fetch_stats] salvo em {out_path}")


if __name__ == "__main__":
    main()
