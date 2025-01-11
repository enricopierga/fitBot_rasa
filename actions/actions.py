from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Form, SlotSet

from typing import Any, Text, Dict, List
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

class ValidateFitnessForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fitness_form"

    async def validate_fitness_goal(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate the 'fitness_goal' slot."""
        valid_goals = ["perdere peso", "aumentare la massa muscolare", "migliorare il tono fisico"]
        if slot_value.lower() in valid_goals:
            return {"fitness_goal": slot_value}
        dispatcher.utter_message(text=f"L'obiettivo '{slot_value}' non è valido. Puoi scegliere tra: {', '.join(valid_goals)}.")
        return {"fitness_goal": None}

    async def validate_experience_level(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate the 'experience_level' slot."""
        valid_levels = ["principiante", "intermedio", "avanzato"]
        if slot_value.lower() in valid_levels:
            return {"experience_level": slot_value}
        dispatcher.utter_message(text=f"Il livello '{slot_value}' non è valido. Puoi scegliere tra: {', '.join(valid_levels)}.")
        return {"experience_level": None}

    async def validate_availability(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate the 'availability' slot."""
        try:
            hours = int(slot_value)
            if hours > 0:
                return {"availability": hours}
        except ValueError:
            pass
        dispatcher.utter_message(text="Inserisci un numero valido di ore per settimana.")
        return {"availability": None}
    
class ActionSubmitFitnessForm(Action):

    def name(self) -> str:
        return "action_submit_fitness_form"

    def run(self, dispatcher, tracker, domain):
        fitness_goal = tracker.get_slot("fitness_goal")
        experience_level = tracker.get_slot("experience_level")
        availability = tracker.get_slot("availability")

        # L'azione finale per il form
        dispatcher.utter_message(text="Grazie! Ora conosco meglio i tuoi obiettivi. Posso creare un piano personalizzato per te!")
        
        # Disattiva il form e opzionalmente resettare slot
        return [Form(None), SlotSet("requested_slot", None)]   
    
    

class ActionCreatePersonalizedWorkout(Action):

    def name(self) -> str:
        return "action_create_personalized_workout"

    def run(self, dispatcher, tracker, domain):
        # Recupera i valori delle slot dal form
        fitness_goal = tracker.get_slot("fitness_goal")
        experience_level = tracker.get_slot("experience_level")
        availability = tracker.get_slot("availability")

        # Trasforma il valore di availability in un numero (se possibile)
        try:
            availability = int(availability)
        except ValueError:
            availability = 0  # Default in caso di errore

        # Genera il piano in base ai valori
        workout_plan = ""

        if fitness_goal == "perdere peso":
            if experience_level == "principiante":
                workout_plan = f"Con {availability} ore disponibili, ti consiglio un programma di cardio leggero combinato con esercizi a corpo libero per principianti."
            elif experience_level == "intermedio":
                workout_plan = f"Con {availability} ore disponibili, puoi seguire un programma di allenamento HIIT e cardio moderato con esercizi di resistenza."
            elif experience_level == "avanzato":
                workout_plan = f"Con {availability} ore disponibili, puoi seguire un programma avanzato di allenamenti combinati cardio e pesistica con alta intensità."

        elif fitness_goal == "aumentare la massa muscolare":
            if experience_level == "principiante":
                workout_plan = f"Con {availability} ore disponibili, inizia con esercizi base di pesistica per sviluppare la tecnica e costruire forza."
            elif experience_level == "intermedio":
                workout_plan = f"Con {availability} ore disponibili, puoi seguire un programma di ipertrofia muscolare con focus su gruppi muscolari specifici."
            elif experience_level == "avanzato":
                workout_plan = f"Con {availability} ore disponibili, segui un programma avanzato con allenamenti giornalieri mirati a gruppi muscolari specifici."

        elif fitness_goal == "migliorare il tono fisico":
            if experience_level == "principiante":
                workout_plan = f"Con {availability} ore disponibili, combina esercizi di resistenza leggeri con stretching e allenamenti a corpo libero."
            elif experience_level == "intermedio":
                workout_plan = f"Con {availability} ore disponibili, puoi seguire un programma di tonificazione con pesi moderati e allenamenti funzionali."
            elif experience_level == "avanzato":
                workout_plan = f"Con {availability} ore disponibili, segui un programma intenso di allenamenti funzionali e resistenza avanzata."

        # Messaggio di default se non ci sono corrispondenze
        if not workout_plan:
            workout_plan = "Non sono riuscito a generare un piano personalizzato. Fornisci maggiori dettagli sui tuoi obiettivi."

        # Invia il messaggio al bot
        dispatcher.utter_message(text=f"Ecco il tuo piano di allenamento personalizzato:\n{workout_plan}")

        return []
    
class ActionAskMoreDetails(Action):

    def name(self) -> str:
        return "utter_ask_more_details"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Vuoi sapere di più su esercizi specifici o consigli per il tuo piano?")
        return []

class ActionProvideExercises(Action):

    def name(self) -> str:
        return "action_provide_exercises"

    def run(self, dispatcher, tracker, domain):
        # Recupera le risposte dal form
        fitness_goal = tracker.get_slot("fitness_goal")
        experience_level = tracker.get_slot("experience_level")
        availability = tracker.get_slot("availability")

        # Trasforma il valore di availability in un numero
        try:
            availability = int(availability)
        except ValueError:
            availability = 0  # Default in caso di errore

        # Logica per generare esercizi
        if fitness_goal == "perdere peso":
            if experience_level == "principiante":
                exercises = """
                - **Cardio leggero**: Camminata veloce (20-30 minuti al giorno). Mantieni una velocità che ti permette di parlare ma non di cantare.
                - **Esercizi a corpo libero**:
                  - Squat (3 serie da 12-15 ripetizioni): Mantieni i talloni a terra e abbassati fino a quando le cosce sono parallele al pavimento.
                  - Affondi (3 serie per gamba): Fai un passo avanti e abbassa il corpo fino a creare un angolo di 90 gradi con entrambe le gambe.
                  - Mountain climbers (3 serie da 20 secondi): Porta le ginocchia al petto alternandole rapidamente.
                - **Consiglio**: Focalizzati sulla costanza, non sull'intensità. Aumenta gradualmente la durata e aggiungi piccoli pesi alle caviglie per intensificare.
                """
            elif experience_level == "intermedio":
                exercises = """
                - **Cardio moderato**:
                  - Corsa leggera o cyclette (30-40 minuti): Includi 1 minuto di corsa veloce ogni 5 minuti per aumentare la combustione calorica.
                - **Esercizi combinati**:
                  - Burpees (3 serie da 12): Salta verso l'alto, scendi in posizione di plank e torna in piedi.
                  - Plank dinamico (3 serie da 20 secondi): Alterna il sollevamento delle braccia durante il plank.
                  - Squat con salto (3 serie da 12): Esegui un normale squat, ma aggiungi un salto esplosivo verso l'alto.
                - **Consiglio**: Integra un allenamento HIIT (High Intensity Interval Training) di 20 minuti per massimizzare la perdita di peso.
                """
            elif experience_level == "avanzato":
                exercises = """
                - **Cardio intenso**:
                  - Interval training: 1 minuto di sprint seguito da 2 minuti di corsa lenta, ripetuto per 20-30 minuti.
                - **Esercizi di resistenza**:
                  - Deadlift (3 serie da 8): Solleva il bilanciere mantenendo la schiena dritta.
                  - Kettlebell swings (3 serie da 15): Solleva il kettlebell con un movimento esplosivo dalle anche.
                  - Push-up esplosivi (3 serie da 12): Salta con le mani dal pavimento in ogni ripetizione.
                - **Consiglio**: Combina pesistica e cardio in circuiti ad alta intensità, includendo poco tempo di recupero tra le serie.
                """

        elif fitness_goal == "aumentare la massa muscolare":
            if experience_level == "principiante":
                exercises = """
                - **Pesistica base**:
                  - Squat con manubri (3 serie da 10): Usa pesi leggeri per abituarti al movimento.
                  - Panca piana con manubri (3 serie da 8-10): Solleva i manubri sopra il petto con controllo.
                  - Rematore con bilanciere (3 serie da 8-10): Tieni la schiena dritta mentre tiri il bilanciere verso l'addome.
                - **Esercizi complementari**:
                  - Sollevamento laterale per le spalle (3 serie da 12): Usa manubri leggeri per allenare i deltoidi.
                  - Curl per bicipiti (3 serie da 12): Solleva i manubri verso le spalle lentamente.
                - **Consiglio**: Concentrati sulla tecnica e aumenta progressivamente il carico ogni 2 settimane.
                """
            elif experience_level == "intermedio":
                exercises = """
                - **Split routine**:
                  - Giorni alterni per petto/tricipiti, schiena/bicipiti, gambe/spalle.
                - **Esercizi base**:
                  - Bench press (3 serie da 6-8): Usa il bilanciere e mantieni i gomiti a 90 gradi.
                  - Squat profondo (3 serie da 10-12): Scendi il più possibile senza perdere la postura corretta.
                  - Pull-up (3 serie da massimo ripetizioni): Usa un elastico se necessario.
                  - Deadlift (3 serie da 8): Mantieni il carico vicino al corpo durante il movimento.
                - **Consiglio**: Introduci superserie (due esercizi consecutivi senza pausa) per aumentare l'intensità.
                """
            elif experience_level == "avanzato":
                exercises = """
                - **Programma avanzato**:
                  - Allenamenti giornalieri mirati a gruppi muscolari specifici (es. push-pull-legs).
                - **Esercizi compound**:
                  - Stacco da terra (4 serie da 5): Usa un peso elevato e lavora sulla forza.
                  - Military press (3 serie da 6-8): Solleva il bilanciere sopra la testa mantenendo una posizione stabile.
                  - Squat con bilanciere (3 serie da 6): Mantieni un peso pesante per lo sviluppo muscolare.
                - **Consiglio**: Integra esercizi di isolamento (es. leg curl, pec deck) per rifinire dettagli muscolari.
                """

        elif fitness_goal == "migliorare il tono fisico":
            if experience_level == "principiante":
                exercises = """
                - **Resistenza leggera**:
                  - Elastici per glutei (3 serie da 15): Usa bande elastiche per resistenza.
                  - Affondi laterali (3 serie da 12 per gamba): Alterna i lati per migliorare l'equilibrio.
                  - Crunch (3 serie da 15): Solleva le spalle verso le ginocchia.
                - **Stretching dinamico**:
                  - Yoga leggero o Pilates: Dedica 20-30 minuti a sessioni leggere di stretching.
                - **Consiglio**: Alterna allenamenti leggeri a giorni di stretching e mobilità.
                """
            elif experience_level == "intermedio":
                exercises = """
                - **Allenamento funzionale**:
                  - Kettlebell swing (3 serie da 15): Usa un movimento esplosivo per sollevare il kettlebell.
                  - Push-up con variazioni (3 serie da 10-12): Alterna push-up classici e diamantati.
                  - Squat con salto (3 serie da 12): Aggiungi esplosività ai movimenti.
                - **Stretching e core**:
                  - Plank laterale (3 serie da 30 secondi per lato): Mantieni il corpo in linea.
                  - Esercizi di stabilità su fitball (3 serie da 12).
                - **Consiglio**: Lavora sull'equilibrio tra forza, resistenza e flessibilità.
                """
            elif experience_level == "avanzato":
                exercises = """
                - **Functional training avanzato**:
                  - TRX (3 serie da 12): Usa il TRX per esercizi come pull-up e squat.
                  - Box jump (3 serie da 10): Salta su una scatola o un gradino alto.
                  - Farmer's carry (3 serie da 30 secondi): Cammina tenendo pesi pesanti in ogni mano.
                - **Core avanzato**:
                  - Dragon flag (3 serie da 8): Un esercizio avanzato per l'addome.
                  - Ab rollout (3 serie da 10): Usa una ruota per allenare il core.
                  - Hollow hold (3 serie da 30 secondi): Mantieni la posizione in isometria.
                - **Consiglio**: Integra sessioni ad alta intensità con stretching profondo per evitare rigidità muscolare.
                """

        # Default se non ci sono corrispondenze
        else:
            exercises = "Non ho abbastanza informazioni per creare esercizi specifici. Prova a fornire dettagli più precisi sui tuoi obiettivi."

        # Invia gli esercizi al bot
        dispatcher.utter_message(text=f"Ecco alcuni esercizi per te:\n{exercises}")
        return []
