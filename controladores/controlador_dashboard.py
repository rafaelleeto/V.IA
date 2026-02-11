from flask import Blueprint, request, render_template, redirect, session, flash, send_file
from modelos import Moderador, Cliente, Acesso, Cartao
from sqlalchemy import func, cast, Date
from datetime import date, datetime, timedelta
import json
import urllib.parse

dashboard_blueprint = Blueprint(
    "dashboard", __name__, template_folder="../vistas/templates")


@dashboard_blueprint.before_request
def admin_before_request():
    if session.get("usuario") is None:
        flash("Você não está logado", "danger")
        return redirect("/")
    moderador = Moderador.query.filter_by(id=session.get("usuario")).first()
    print(moderador.nome)
    if moderador.admin == False:
        flash("Você não tem permissões", "danger")
        return redirect("/painel")


@dashboard_blueprint.route("/painel/admin/dashboard")
def dashboard():
    grafico_moderador = criar_grafico_moderador()
    grafico_tipo_cliente = criar_grafico_tipo_cliente()
    acessos_hoje = pegar_acessos_hoje()
    print(acessos_hoje)
    todos_clientes = pegar_todos_clientes()
    cartoes_ativos_porcentagem = cartoes_ativos()
    grafico_geral = criar_grafico_geral()
    return render_template("dashboard.html", grafico_moderador=grafico_moderador, grafico_tipo_cliente=grafico_tipo_cliente,
                           acessos_hoje=acessos_hoje, todos_clientes=todos_clientes, cartoes_ativos_porcentagem=cartoes_ativos_porcentagem,
                           grafico_geral=grafico_geral
                           )


def criar_grafico(dicionario_grafico, w=800, h=600):
    return f"https://quickchart.io/chart?c={urllib.parse.quote(json.dumps(dicionario_grafico))}&w={w}&h={h}&format=svg"


def criar_grafico_moderador():
    moderadores_ativos = Moderador.query.filter_by(ativo=True).count()
    moderadores_inativos = Moderador.query.filter_by(ativo=False).count()
    grafico = {
        "type": "outlabeledPie",
        "data": {
            "labels": ["Moderadores ativos", "Moderadores inativos"],
            "datasets": [{
                "backgroundColor": ["#1996C7", "#C52727"],
                "data": [moderadores_ativos, moderadores_inativos]
            }]
        },
        "options": {
            "plugins": {
                "legend": False,
                "outlabels": {
                    "text": "%l %p",
                    "color": "white",
                    "stretch": 35,
                    "font": {
                        "resizable": True,
                        "minSize": 12,
                        "maxSize": 18
                    }
                }
            }
        }
    }
    return criar_grafico(grafico)


def criar_grafico_tipo_cliente():
    alunos = Cliente.query.filter_by(tipo="aluno").count()
    professores = Cliente.query.filter_by(tipo="professor").count()
    visitantes = Cliente.query.filter_by(tipo="visitante").count()
    grafico = {
        "type": "bar",
        "data": {
            "labels": [
                "Visitantes",
                "Alunos",
                "Professores",
            ],
            "datasets": [
                {
                    "label": "Dataset 1",
                    "backgroundColor": ["rgba(52, 152, 219, 0.8)", "rgba(46, 204, 113, 0.8)", "rgba(230, 126, 34, 0.8)"],
                    "borderWidth": 1,
                    "data": [
                        visitantes,
                        alunos,
                        professores,
                    ]
                },
            ]
        },
        "options": {
            "scales": {
                "yAxes": [
                    {
                        "ticks": {
                            "min": 0,
                            "max": max(visitantes, alunos, professores) + 1,
                            "precision": 0,
                        }
                    }
                ]
            },
            "responsive": True,
            "legend": {
                "display": False
            },
            "plugins": {

                "roundedBars": True
            }
        }
    }
    return criar_grafico(grafico)


def criar_grafico_geral():
    administradores = Moderador.query.filter_by(admin=True).count()
    moderadores = Moderador.query.filter_by(admin=False).count()
    alunos = Cliente.query.filter_by(tipo="aluno").count()
    professores = Cliente.query.filter_by(tipo="professor").count()
    visitantes = Cliente.query.filter_by(tipo="visitante").count()

    grafico = {
        "type": "doughnut",
        "data": {
            "datasets": [
                {
                    "data": [administradores, moderadores, alunos, professores, visitantes],
                    "backgroundColor": [
                        "rgb(255, 99, 132)",
                        "rgb(255, 159, 64)",
                        "rgb(255, 205, 86)",
                        "rgb(75, 192, 192)",
                        "rgb(54, 162, 235)"
                    ],
                    "label": "Dataset 1"
                }
            ],
            "labels": ["Administradores", "Moderadores", "Alunos", "Professores", "Visitantes"]
        },
        "options": {
            "title": {
                "display": False,
                "text": "Chart.js Doughnut Chart"
            }
        }
    }
    return criar_grafico(grafico, w=400, h=200)


def pegar_acessos_hoje():
    hoje = datetime.combine(date.today(), datetime.min.time())
    amanha = hoje + timedelta(days=1)
    total_acessos = Acesso.query.filter(
        Acesso.data_criacao >= hoje,
        Acesso.data_criacao < amanha
    ).count()

    return total_acessos


def pegar_todos_clientes():
    clientes = Cliente.query.count()
    return clientes


def cartoes_ativos():
    inativos = Cartao.query.filter_by(tem_acesso=False).count()
    total = Cartao.query.count()
    if total == 0:
        return 0.0
    ativos = total - inativos
    porcentagem = (ativos/total) * 100
    return porcentagem
