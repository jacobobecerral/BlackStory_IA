import argparse
import asyncio
import json
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from rich.live import Live
from dotenv import load_dotenv

from game_prompts import (
    PROMPT_SISTEMA_COMUN,
    PROMPT_SISTEMA_NARRADOR,
    PROMPT_SISTEMA_INVESTIGADOR,
    PROMPT_NARRADOR_GENERADOR,
    PROMPT_INVESTIGADOR,
    PROMPT_NARRADOR_RESPUESTA,
    PROMPT_NARRADOR_JUEZ,
    PROMPT_INVESTIGADOR_RESOLUCION,
)
from ai_providers import get_ai_provider, AIProvider

console = Console()

async def main():
    load_dotenv() # Load environment variables from .env file
    parser = argparse.ArgumentParser(description="BlackStory AI: An AI-driven mystery game.")
    parser.add_argument(
        "-pn", "--provider-narrador",
        choices=["ollama", "gemini", "anthropic", "openai"],
        default="gemini",
        help="Proveedor de la IA Narradora."
    )
    parser.add_argument(
        "-mn", "--model-narrador",
        default="gemini-1.5-flash",
        help="Nombre del modelo para el Narrador."
    )
    parser.add_argument(
        "-pi", "--provider-investigador",
        choices=["ollama", "gemini", "anthropic", "openai"],
        default="gemini",
        help="Proveedor de la IA Investigadora."
    )
    parser.add_argument(
        "-mi", "--model-investigador",
        default="gemini-1.5-flash",
        help="Nombre del modelo para el Investigador."
    )
    parser.add_argument(
        "--turnos",
        type=int,
        default=15,
        help="Número máximo de turnos (preguntas) antes de revelar la solución."
    )

    args = parser.parse_args()

    # Check for API keys after loading environment variables
    if args.provider_narrador == "gemini" or args.provider_investigador == "gemini":
        if not os.getenv("GOOGLE_API_KEY"):
            console.print("[bold red]Error: GOOGLE_API_KEY no encontrada en .env. Por favor, crea un archivo .env y añade tu clave API de Gemini.[/bold red]")
            return
    if args.provider_narrador == "openai" or args.provider_investigador == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[bold red]Error: OPENAI_API_KEY no encontrada en .env. Por favor, crea un archivo .env y añade tu clave API de OpenAI.[/bold red]")
            return
    if args.provider_narrador == "anthropic" or args.provider_investigador == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            console.print("[bold red]Error: ANTHROPIC_API_KEY no encontrada en .env. Por favor, crea un archivo .env y añade tu clave API de Anthropic.[/bold red]")
            return

    narrador_provider: AIProvider = get_ai_provider(args.provider_narrador, args.model_narrador)
    investigador_provider: AIProvider = get_ai_provider(args.provider_investigador, args.model_investigador)

    console.print(Panel(Text("[bold blue]Iniciando BlackStory AI[/bold blue]", justify="center")))
    console.print(f"Narrador: [bold green]{args.provider_narrador} ({args.model_narrador})[/bold green]")
    console.print(f"Investigador: [bold yellow]{args.provider_investigador} ({args.model_investigador})[/bold yellow]")
    console.print(f"Turnos máximos: [bold magenta]{args.turnos}[/bold magenta]\n")

    # Fase 1: Creación del Misterio
    enigma = ""
    solucion_secreta = ""
    with Live(Spinner("dots", text="[bold green]Narrador pensando el misterio...[/bold green]"), console=console, transient=True) as live:
        try:
            narrador_response = await narrador_provider.generate_json(
                system_prompt=PROMPT_SISTEMA_COMUN + "\n" + PROMPT_SISTEMA_NARRADOR,
                user_prompt=PROMPT_NARRADOR_GENERADOR
            )
            enigma = narrador_response["enigma"]
            solucion_secreta = narrador_response["solucion"]
            live.stop()
            console.print("[bold green]Misterio creado![/bold green]\n")
        except Exception as e:
            live.stop()
            console.print(f"[bold red]Error al crear el misterio: {e}[/bold red]")
            return

    # Fase 2: Investigación (El Bucle)
    console.print(Panel(Text(f"[bold blue]Enigma:[/bold blue]\n{enigma}", justify="left"), title="[bold blue]El Misterio[/bold blue]", title_align="left", border_style="blue"))
    console.print("\n[bold cyan]Comienza la investigación...[/bold cyan]\n")

    historial_chat = []
    for turno in range(1, args.turnos + 1):
        console.print(f"\n[bold white]--- Turno {turno}/{args.turnos} ---[/bold white]")

        # a. Turno del Investigador
        investigador_question = ""
        with Live(Spinner("dots", text=f"[bold yellow]Investigador ({args.model_investigador}) pensando...[/bold yellow]"), console=console, transient=True) as live:
            try:
                investigador_question = await investigador_provider.generate_text(
                    system_prompt=PROMPT_SISTEMA_COMUN + "\n" + PROMPT_SISTEMA_INVESTIGADOR,
                    user_prompt=PROMPT_INVESTIGADOR.format(enigma=enigma, historial_chat="\n".join(historial_chat))
                )
                live.stop()
                console.print(f"[bold yellow]Investigador:[/bold yellow] {investigador_question}")
            except Exception as e:
                live.stop()
                console.print(f"[bold red]Error Investigador: {e}[/bold red]")
                break

        # b. Turno del Narrador
        narrador_answer = ""
        with Live(Spinner("dots", text=f"[bold green]Narrador ({args.model_narrador}) evaluando...[/bold green]"), console=console, transient=True) as live:
            try:
                raw_answer = await narrador_provider.generate_text(
                    system_prompt=PROMPT_SISTEMA_COMUN + "\n" + PROMPT_SISTEMA_NARRADOR,
                    user_prompt=PROMPT_NARRADOR_RESPUESTA.format(
                        solucion_secreta=solucion_secreta,
                        pregunta_investigador=investigador_question
                    )
                )
                # Validación estricta de la respuesta del Narrador
                if raw_answer.lower().strip() in ["sí", "si", "no", "no es relevante"]:
                    narrador_answer = raw_answer.lower().strip()
                else:
                    narrador_answer = "no es relevante" # Forzar a una respuesta válida si el LLM se desvía
                live.stop()
                console.print(f"[bold green]Narrador:[/bold green] {narrador_answer}")
            except Exception as e:
                live.stop()
                console.print(f"[bold red]Error Narrador: {e}[/bold red]")
                break

        # c. Actualización de Estado
        # Solo añadir al historial si ambos se generaron correctamente
        if investigador_question and narrador_answer:
            historial_chat.append(f"Investigador: {investigador_question}")
            historial_chat.append(f"Narrador: {narrador_answer}")
        else:
            # Si uno de los dos falló, no se añade nada para este turno
            console.print("[bold red]Turno incompleto debido a un error. No se añade al historial.[/bold red]")


    # Fase 3: Revelación (El Final)
    console.print(Panel(Text("[bold blue]--- FIN DE LA PARTIDA ---[/bold blue]", justify="center")))
    console.print(Panel(Text(f"[bold magenta]Solución Secreta:[/bold magenta]\n{solucion_secreta}", justify="left"), title="[bold magenta]La Verdad Revelada[/bold magenta]", title_align="left", border_style="magenta"))

    # Fase 3.1: Resolución del Investigador
    investigador_resolucion = ""
    with Live(Spinner("dots", text=f"[bold yellow]Investigador ({args.model_investigador}) formulando resolución final...[/bold yellow]"), console=console, transient=True) as live:
        try:
            investigador_resolucion = await investigador_provider.generate_text(
                system_prompt=PROMPT_SISTEMA_COMUN + "\n" + PROMPT_SISTEMA_INVESTIGADOR,
                user_prompt=PROMPT_INVESTIGADOR_RESOLUCION.format(enigma=enigma, historial_chat="\n".join(historial_chat))
            )
            live.stop()
            console.print(Panel(f"[bold yellow]Resolución del Investigador:[/bold yellow]\n{investigador_resolucion}", title="[bold yellow]Hipótesis Final[/bold yellow]", title_align="left", border_style="yellow"))
            historial_chat.append(f"Investigador (Resolución Final): {investigador_resolucion}")
        except Exception as e:
            live.stop()
            console.print(f"[bold red]Error al obtener la resolución del Investigador: {e}[/bold red]")
            investigador_resolucion = "ERROR_RESOLUCION"

    # Juicio Final
    veredicto = ""
    with Live(Spinner("dots", text=f"[bold green]Narrador ({args.model_narrador}) emitiendo veredicto...[/bold green]"), console=console, transient=True) as live:
        try:
            raw_veredicto = await narrador_provider.generate_text(
                system_prompt=PROMPT_SISTEMA_NARRADOR, # Solo el prompt del narrador para el juicio
                user_prompt=PROMPT_NARRADOR_JUEZ.format(
                    solucion_secreta=solucion_secreta,
                    historial_chat="\n".join(historial_chat) + f"\nResolución del Investigador: {investigador_resolucion}"
                )
            )
            if raw_veredicto.upper().strip() in ["GANADOR", "PERDEDOR"]:
                veredicto = raw_veredicto.upper().strip()
            else:
                veredicto = "PERDEDOR" # Forzar a un veredicto válido
            live.stop()
            console.print(f"\n[bold yellow]Veredicto: {veredicto}[/bold yellow]")
        except Exception as e:
            live.stop()
            console.print(f"[bold red]Error al emitir veredicto: {e}[/bold red]")
            veredicto = "ERROR"

    # Guardado
    os.makedirs("./historial_partidas", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"./historial_partidas/partida_{timestamp}.md"

    mermaid_content = f"""
graph TD
    subgraph Misterio
        A[Enigma] --> B(Solución Secreta)
    end

    subgraph Investigación
        B -- Conocida por Narrador --> C(Narrador)
        A -- Conocida por Investigador --> D(Investigador)
    end

    subgraph Turnos
"""
    for i in range(0, len(historial_chat), 2):
        if i + 1 < len(historial_chat): # Ensure there's a corresponding answer
            question = historial_chat[i].replace("Investigador: ", "")
            answer = historial_chat[i+1].replace("Narrador: ", "")
            mermaid_content += f"        D -- Pregunta {i//2 + 1}: {question} --> C\n"
            mermaid_content += f"        C -- Respuesta {i//2 + 1}: {answer} --> D\n"
        else:
            console.print(f"[bold red]Advertencia: Historial de chat incompleto en el turno {i//2 + 1}. Se omitirá del diagrama.[/bold red]")

    mermaid_content += f"""
    end

    subgraph Resultado
        D -- Veredicto: {veredicto} --> E(Fin de Partida)
    end
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# BlackStory AI - Transcripción de Partida\n\n")
        f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Narrador:** {args.provider_narrador} ({args.model_narrador})\n")
        f.write(f"**Investigador:** {args.provider_investigador} ({args.model_investigador})\n")
        f.write(f"**Turnos:** {args.turnos}\n\n")
        f.write(f"## Enigma\n{enigma}\n\n")
        f.write(f"## Solución Secreta\n{solucion_secreta}\n\n")
        f.write("## Historial de Chat\n")
        for line in historial_chat:
            f.write(f"- {line}\n")
        f.write(f"\n## Veredicto Final\n{veredicto}\n\n")
        f.write("## Diagrama de Flujo (Mermaid)\n")
        f.write("```mermaid\n")
        f.write(mermaid_content)
        f.write("```\n")

    console.print(f"\n[bold blue]Transcripción guardada en:[/bold blue] [link=file://{os.path.abspath(filename)}]{filename}[/link]")

if __name__ == "__main__":
    asyncio.run(main())
