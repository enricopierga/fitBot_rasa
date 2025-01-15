from typing import Any, Text, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Form, SlotSet

from typing import Any, Text, Dict
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import AllSlotsReset, Restarted, UserUtteranceReverted

import logging

# Configurazione base del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionStopBot(Action):
    def name(self) -> str:
        return "action_stop_bot"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="Conversazione interrotta. Grazie per avermi usato! 👋"
        )
        return [AllSlotsReset(), Restarted()]

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
        slot_value = slot_value.strip().lower()
        if slot_value in valid_goals:
            return {"fitness_goal": slot_value}
        dispatcher.utter_message(
            text=f"⚠️ L'obiettivo '{slot_value}' non è valido. Puoi scegliere tra: {', '.join(valid_goals)}. 🎯"
        )
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
        slot_value = slot_value.strip().lower()
        if slot_value in valid_levels:
            return {"experience_level": slot_value}
        dispatcher.utter_message(
            text=f"⚠️ Il livello '{slot_value}' non è valido. Puoi scegliere tra: {', '.join(valid_levels)}. 🏋️‍♂️"
        )
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
            if 1 <= hours <= 168:
                return {"availability": hours}
        except ValueError:
            pass
        dispatcher.utter_message(
            text="⏰ Inserisci un numero valido di ore (1-168) per settimana. 🕒"
        )
        return {"availability": None}


class ActionSubmitFitnessForm(Action):
    def name(self) -> str:
        return "action_submit_fitness_form"

    def run(self, dispatcher, tracker, domain):
        fitness_goal = tracker.get_slot("fitness_goal")
        experience_level = tracker.get_slot("experience_level")
        availability = tracker.get_slot("availability")

        # Log dei dati raccolti
        logger.info(f"Obiettivo: {fitness_goal}, Livello: {experience_level}, Ore: {availability}")

        dispatcher.utter_message(
            text="🎉 Grazie! Ora conosco meglio i tuoi obiettivi. Procedo a creare il tuo piano personalizzato! 💪"
        )
        return [Form(None), SlotSet("requested_slot", None)]


class ActionCreatePersonalizedWorkout(Action):
    def name(self) -> str:
        return "action_create_personalized_workout"

    def run(self, dispatcher, tracker, domain):
        # Recupera i valori degli slot dal form
        fitness_goal = tracker.get_slot("fitness_goal")
        experience_level = tracker.get_slot("experience_level")
        availability = tracker.get_slot("availability")

        # Trasforma il valore di availability in un numero
        try:
            availability = int(availability)
        except (ValueError, TypeError):
            availability = 0  # Valore predefinito in caso di errore

        # Genera il piano in base ai valori raccolti
        workout_plan = self._generate_workout_plan(fitness_goal, experience_level, availability)

        # Messaggio di default se non è stato possibile generare un piano
        if not workout_plan:
            workout_plan = "❌ Non sono riuscito a generare un piano personalizzato. Per favore, fornisci maggiori dettagli sui tuoi obiettivi. 😊"

        # Invia il piano generato come messaggio al bot
        dispatcher.utter_message(
            text=f"📋 Ecco il tuo piano di allenamento personalizzato:\n{workout_plan} 🏋️‍♀️"
        )
        return []

    def _generate_workout_plan(self, fitness_goal, experience_level, availability):
        """
        Logica per generare un piano personalizzato in base agli slot raccolti.
        """
        if not fitness_goal or not experience_level or availability <= 0:
            return None

        # Piani per perdere peso
        if fitness_goal == "perdere peso":
            return self._generate_weight_loss_plan(experience_level, availability)

        # Piani per aumentare la massa muscolare
        elif fitness_goal == "aumentare la massa muscolare":
            return self._generate_muscle_gain_plan(experience_level, availability)

        # Piani per migliorare il tono fisico
        elif fitness_goal == "migliorare il tono fisico":
            return self._generate_tone_plan(experience_level, availability)

        return None

    def _generate_weight_loss_plan(self, experience_level, availability):
        """
        Genera un piano per perdere peso.
        """
        plans = {
            "principiante": f"⏳ Con {availability} ore disponibili, ti consiglio un programma di cardio leggero combinato con esercizi a corpo libero per principianti. 🏃‍♂️",
            "intermedio": f"🔥 Con {availability} ore disponibili, puoi seguire un programma di allenamento HIIT e cardio moderato con esercizi di resistenza. 🚴‍♀️",
            "avanzato": f"💪 Con {availability} ore disponibili, puoi seguire un programma avanzato di allenamenti combinati cardio e pesistica con alta intensità. 🏋️‍♂️"
        }
        return plans.get(experience_level)

    def _generate_muscle_gain_plan(self, experience_level, availability):
        """
        Genera un piano per aumentare la massa muscolare.
        """
        plans = {
            "principiante": f"🛠️ Con {availability} ore disponibili, inizia con esercizi base di pesistica per sviluppare la tecnica e costruire forza. 💪",
            "intermedio": f"🔩 Con {availability} ore disponibili, puoi seguire un programma di ipertrofia muscolare con focus su gruppi muscolari specifici. 🏋️‍♀️",
            "avanzato": f"🏆 Con {availability} ore disponibili, segui un programma avanzato con allenamenti giornalieri mirati a gruppi muscolari specifici. 🏋️‍♂️"
        }
        return plans.get(experience_level)

    def _generate_tone_plan(self, experience_level, availability):
        """
        Genera un piano per migliorare il tono fisico.
        """
        plans = {
            "principiante": f"🌱 Con {availability} ore disponibili, combina esercizi di resistenza leggeri con stretching e allenamenti a corpo libero. 🤸‍♂️",
            "intermedio": f"🌟 Con {availability} ore disponibili, puoi seguire un programma di tonificazione con pesi moderati e allenamenti funzionali. 🏋️‍♀️",
            "avanzato": f"💥 Con {availability} ore disponibili, segui un programma intenso di allenamenti funzionali e resistenza avanzata. 🔥"
        }
        return plans.get(experience_level)


class ActionAskMoreDetails(Action):
    def name(self) -> str:
        return "utter_ask_more_details"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="🔎 Vuoi sapere di più su esercizi specifici o consigli per il tuo piano? 💡"
        )
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
                💪 **Cardio leggero**: Camminata veloce (20-30 minuti al giorno). Mantieni una velocità che ti permette di parlare ma non di cantare.
                🏋️‍♀️ **Esercizi a corpo libero**:
                  🔹 Squat (3 serie da 12-15 ripetizioni): Mantieni i talloni a terra e abbassati fino a quando le cosce sono parallele al pavimento.
                  🔹 Affondi (3 serie per gamba): Fai un passo avanti e abbassa il corpo fino a creare un angolo di 90 gradi con entrambe le gambe.
                  🔹 Mountain climbers (3 serie da 20 secondi): Porta le ginocchia al petto alternandole rapidamente.
                🌟 **Consiglio**: Focalizzati sulla costanza, non sull'intensità. Aumenta gradualmente la durata e aggiungi piccoli pesi alle caviglie per intensificare.
                """
            elif experience_level == "intermedio":
                exercises = """
                🏃‍♀️ **Cardio moderato**:
                  🔹 Corsa leggera o cyclette (30-40 minuti): Includi 1 minuto di corsa veloce ogni 5 minuti per aumentare la combustione calorica.
                🤸‍♀️ **Esercizi combinati**:
                  🔹 Burpees (3 serie da 12): Salta verso l'alto, scendi in posizione di plank e torna in piedi.
                  🔹 Plank dinamico (3 serie da 20 secondi): Alterna il sollevamento delle braccia durante il plank.
                  🔹 Squat con salto (3 serie da 12): Esegui un normale squat, ma aggiungi un salto esplosivo verso l'alto.
                🚀 **Consiglio**: Integra un allenamento HIIT (High Intensity Interval Training) di 20 minuti per massimizzare la perdita di peso.
                """
            elif experience_level == "avanzato":
                exercises = """
                🏋️‍♂️ **Cardio intenso**:
                  🔹 Interval training: 1 minuto di sprint seguito da 2 minuti di corsa lenta, ripetuto per 20-30 minuti.
                🏋️‍♀️ **Esercizi di resistenza**:
                  🔹 Deadlift (3 serie da 8): Solleva il bilanciere mantenendo la schiena dritta.
                  🔹 Kettlebell swings (3 serie da 15): Solleva il kettlebell con un movimento esplosivo dalle anche.
                  🔹 Push-up esplosivi (3 serie da 12): Salta con le mani dal pavimento in ogni ripetizione.
                💥 **Consiglio**: Combina pesistica e cardio in circuiti ad alta intensità, includendo poco tempo di recupero tra le serie.
                """

        elif fitness_goal == "aumentare la massa muscolare":
            if experience_level == "principiante":
                exercises = """
                🏋️‍♀️ **Pesistica base**:
                  🔹 Squat con manubri (3 serie da 10): Usa pesi leggeri per abituarti al movimento.
                  🔹 Panca piana con manubri (3 serie da 8-10): Solleva i manubri sopra il petto con controllo.
                  🔹 Rematore con bilanciere (3 serie da 8-10): Tieni la schiena dritta mentre tiri il bilanciere verso l'addome.
                🔧 **Esercizi complementari**:
                  🔹 Sollevamento laterale per le spalle (3 serie da 12): Usa manubri leggeri per allenare i deltoidi.
                  🔹 Curl per bicipiti (3 serie da 12): Solleva i manubri verso le spalle lentamente.
                🏆 **Consiglio**: Concentrati sulla tecnica e aumenta progressivamente il carico ogni 2 settimane.
                """
            # Aggiungi altre opzioni come sopra...

        # Default se non ci sono corrispondenze
        else:
            exercises = "🤔 Non ho abbastanza informazioni per creare esercizi specifici. Prova a fornire dettagli più precisi sui tuoi obiettivi."

        # Invia gli esercizi al bot
        dispatcher.utter_message(text=f"🎉 **Ecco alcuni esercizi per te**:\n{exercises}")
        return []

    
class ActionGoodbye(Action):
    def name(self) -> str:
        return "utter_goodbye"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Grazie per avermi usato! A presto e buon allenamento!")
        return []
    
class ActionDefaultFallback(Action):
    def name(self) -> str:
        return "action_default_fallback"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="Mi dispiace, non ho capito la tua richiesta. Puoi riformularla o chiedermi qualcosa di diverso? 😊"
        )
        return []


class ActionResetSlots(Action):
    def name(self) -> str:
        return "action_reset_slots"

    def run(self, dispatcher, tracker, domain):
        # Reset di tutti gli slot
        slots_to_reset = ["fitness_goal", "experience_level", "availability"]
        return [SlotSet(slot, None) for slot in slots_to_reset]
    
class ActionHandleFallback(Action):
    def name(self):
        return "action_handle_fallback"

    def run(self, dispatcher, tracker, domain):
        fallback_count = tracker.get_slot("fallback_count")
        
        # Incrementa il contatore di fallback
        if fallback_count is None:
            fallback_count = 0
        fallback_count += 1

        # Controlla il numero di fallback consecutivi
        if fallback_count >= 3:
            dispatcher.utter_message(
                text="Sembra che non riesca a capire la tua richiesta. 😓 Interrompo la conversazione. "
                     "Puoi sempre riprovare più tardi! 🙏"
            )
            # Resetta il contatore e termina la conversazione
            return [SlotSet("fallback_count", 0)]
        else:
            dispatcher.utter_message(
                text="Mi dispiace, non ho capito la tua richiesta. Puoi riformularla o chiedermi qualcosa di diverso? 😊"
            )
            return [SlotSet("fallback_count", fallback_count), UserUtteranceReverted()]