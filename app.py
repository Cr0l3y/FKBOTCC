# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import traceback
from datetime import datetime

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from bot import MyBot
from config import DefaultConfig

CONFIG = DefaultConfig()

# Cria adaptador.
# Consulte https://aka.ms/about-bot-adapter para saber mais sobre como os bots funcionam.
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


# Pega tudo para erros.
async def on_error(context: TurnContext, error: Exception):
    # Esta verificação grava os erros no log do console .vs. insights de aplicativos.
    # NOTE: No ambiente de produção, você deve considerar registrar isso no Azure
    #       insights de aplicativos.
    print(f"\n [on_turn_error] erro não tratado: {error}", file=sys.stderr)
    traceback.print_exc()

    #Envia uma mensagem para o usuário
    await context.send_activity("O bot encontrou um erro ou bug.")
    await context.send_activity(
        "Para continuar a executar este bot, corrija o código-fonte do bot."
    )
    # Envie uma atividade de rastreamento se estivermos conversando com o Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Cria uma atividade de rastreamento que contém o objeto de erro
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Envie uma atividade de rastreamento, que será exibida no Bot Framework Emulator
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = on_error

#Cria o bot
BOT = MyBot()


# Ouça as solicitações recebidas em /api/messages
async def messages(req: Request) -> Response:
   # Manipulador de mensagens do bot principal.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=201)


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error

