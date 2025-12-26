import random
import string
from datetime import datetime
from pathlib import Path

from src.agent.state import STATES
from src.agent.prompts import RESPONSES
from src.agent.nlu import parse_user_message
from src.utils.file_store import save_uploads
from src.utils.pdf_generator import generate_birth_certificate_pdf, ensure_generated_dir


class KebeleAgent:
    def __init__(self):
        self.sessions = {}  # user_id -> session dict

    def _gen_ref(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def _validate_date(self, s: str) -> bool:
        try:
            d, m, y = s.strip().split("/")
            dt = datetime(int(y), int(m), int(d))
            return dt.year == int(y) and dt.month == int(m) and dt.day == int(d)
        except Exception:
            return False

    def start(self, user_id: str, language: str = "am"):
        self.sessions[user_id] = {
            "state": STATES.GREETING,
            "language": language,
            "service": None,  # birth_certificate | id_appointment
            "data": {},
        }
        return {"response": RESPONSES[language]["greeting"], "nextAction": "button_choice", "options": ["A", "B"]}

    def _apply_fields(self, data: dict, fields: dict, state: str):
        """Apply extracted fields to session data, only if they're relevant."""
        # Normalize and apply fields
        for field_name, value in fields.items():
            if not value:  # Skip empty values
                continue
                
            # Normalize sex field
            if field_name == "sex":
                sex_lower = str(value).lower()
                if sex_lower in ["male", "boy", "m", "ወንድ"]:
                    data["sex"] = "Male"
                elif sex_lower in ["female", "girl", "f", "ሴት"]:
                    data["sex"] = "Female"
                else:
                    data["sex"] = value  # Keep as-is if unclear
            
            # Normalize date format
            elif field_name == "date_of_birth" or field_name == "dob":
                dob_str = str(value).strip()
                # Try to normalize to DD/MM/YYYY
                data["date_of_birth"] = dob_str
            
            # Apply other fields directly
            elif field_name in ["child_name", "father_name", "mother_name", "age", "has_previous_id", "appointment_slot", "print_option"]:
                data[field_name] = value

    def _auto_advance_birth_certificate(self, s: dict, data: dict, lang: dict):
        """Auto-advance through birth certificate states if fields are complete."""
        state = s["state"]
        
        # Check if we can advance from current state
        if state == STATES.BIRTH_CHILD_NAME:
            if data.get("child_name"):
                if not data.get("date_of_birth"):
                    s["state"] = STATES.BIRTH_DOB
                    return {"response": lang["birth_dob"], "nextAction": "input_field", "fieldType": "text"}
        
        if state == STATES.BIRTH_DOB:
            if data.get("date_of_birth"):
                if not self._validate_date(data["date_of_birth"]):
                    return {"response": "Invalid date format. Use DD/MM/YYYY (e.g., 15/03/2020).", "nextAction": "retry"}
                if not data.get("sex"):
                    s["state"] = STATES.BIRTH_SEX
                    return {"response": lang["birth_sex"], "nextAction": "button_choice", "options": ["A", "B"]}
        
        if state == STATES.BIRTH_SEX:
            if data.get("sex"):
                if not data.get("father_name"):
                    s["state"] = STATES.BIRTH_FATHER_NAME
                    return {"response": lang["birth_father_name"], "nextAction": "input_field", "fieldType": "text"}
        
        if state == STATES.BIRTH_FATHER_NAME:
            if data.get("father_name"):
                if not data.get("mother_name"):
                    s["state"] = STATES.BIRTH_MOTHER_NAME
                    return {"response": lang["birth_mother_name"], "nextAction": "input_field", "fieldType": "text"}
        
        if state == STATES.BIRTH_MOTHER_NAME:
            if data.get("mother_name"):
                s["state"] = STATES.BIRTH_DOCUMENTS
                return {"response": lang["birth_documents"], "nextAction": "file_upload", "fieldType": "file"}
        
        return None

    def _auto_advance_id_appointment(self, s: dict, data: dict, lang: dict):
        """Auto-advance through ID appointment states if fields are complete."""
        state = s["state"]
        
        if state == STATES.ID_AGE and data.get("age"):
            if isinstance(data["age"], str):
                try:
                    data["age"] = int(data["age"])
                except:
                    return {"response": "Please enter a number (age).", "nextAction": "retry"}
            if data["age"] < 16:
                return {"response": "You must be at least 16 years old. Enter your age again.", "nextAction": "retry"}
            if "has_previous_id" not in data:
                s["state"] = STATES.ID_HAS_ID
                return {"response": lang["id_has_id"], "nextAction": "button_choice", "options": ["A", "B"]}
        
        if state == STATES.ID_HAS_ID and "has_previous_id" in data:
            if "appointment_slot" not in data:
                s["state"] = STATES.ID_SLOT_SELECTION
                return {"response": lang["id_slot_selection"], "nextAction": "button_choice", "options": ["A", "B", "C", "D"]}
        
        return None

    def process(self, user_id: str, message: str, language: str = "am", files: list = None):
        if user_id not in self.sessions:
            return self.start(user_id, language)

        s = self.sessions[user_id]
        lang = RESPONSES.get(s["language"], RESPONSES["en"])
        msg = (message or "").strip()

        # allow language switching mid-chat
        s["language"] = language
        lang = RESPONSES.get(language, RESPONSES["en"])

        state = s["state"]
        service = s["service"]
        data = s["data"]

        # Handle file uploads deterministically (bypass NLU for files)
        if files and state == STATES.BIRTH_DOCUMENTS:
            if len(files) == 0:
                return {"response": "Please upload at least 1 document (images or PDF) before continuing.", "nextAction": "file_upload", "fieldType": "file"}
            if len(files) > 3:
                return {"response": "Please upload maximum 3 documents.", "nextAction": "file_upload", "fieldType": "file"}
            
            saved_paths = save_uploads(user_id, files)
            if not saved_paths:
                return {"response": "Error saving files. Please try uploading again.", "nextAction": "file_upload", "fieldType": "file"}
            
            data["uploaded_files"] = saved_paths
            data["documents_note"] = msg if msg else f"Documents uploaded ({len(saved_paths)} file(s))"
            s["state"] = STATES.BIRTH_PAYMENT
            return {"response": lang["birth_payment_amount"], "nextAction": "button_choice", "options": ["A", "B"]}

        # Parse user message with NLU (unless it's a simple A/B/C/D choice)
        if msg.upper() in ["A", "B", "C", "D", "DONE"]:
            # Simple choice, handle directly
            cmd = type('obj', (object,), {
                'intent': 'choose_option',
                'choice': msg.upper(),
                'fields': {},
                'service': None,
                'language': None
            })()
        else:
            cmd = parse_user_message(msg, state, language)

        # Handle reset intent
        if cmd.intent == "reset":
            return self.start(user_id, language)

        # Handle service selection
        if cmd.intent == "choose_service" and cmd.service:
            s["service"] = cmd.service
            if cmd.service == "birth_certificate":
                s["state"] = STATES.BIRTH_CHILD_NAME
            else:
                s["state"] = STATES.ID_AGE
            # Apply any fields that were provided with service selection
            self._apply_fields(data, cmd.fields, s["state"])
            # Try auto-advance
            if cmd.service == "birth_certificate":
                auto_result = self._auto_advance_birth_certificate(s, data, lang)
                if auto_result:
                    return auto_result
                return {"response": lang["birth_child_name"], "nextAction": "input_field", "fieldType": "text"}
            else:
                auto_result = self._auto_advance_id_appointment(s, data, lang)
                if auto_result:
                    return auto_result
                return {"response": lang["id_age"], "nextAction": "input_field", "fieldType": "number"}

        # Apply extracted fields to current state
        if cmd.fields:
            self._apply_fields(data, cmd.fields, state)

        # Handle choices
        if cmd.choice:
            msg = cmd.choice

        # ---- Birth certificate flow
        if service == "birth_certificate":
            # Try auto-advance first
            auto_result = self._auto_advance_birth_certificate(s, data, lang)
            if auto_result:
                return auto_result
            
            if state == STATES.BIRTH_CHILD_NAME:
                # Use extracted field or message
                child_name = data.get("child_name") or (msg if msg and not cmd.choice else None)
                if not child_name:
                    return {"response": lang["birth_child_name"], "nextAction": "input_field", "fieldType": "text"}
                data["child_name"] = child_name
                s["state"] = STATES.BIRTH_DOB
                return {"response": lang["birth_dob"], "nextAction": "input_field", "fieldType": "text"}

            if state == STATES.BIRTH_DOB:
                dob = data.get("date_of_birth") or (msg if msg and not cmd.choice else None)
                if not dob:
                    return {"response": lang["birth_dob"], "nextAction": "input_field", "fieldType": "text"}
                if not self._validate_date(dob):
                    return {"response": "Invalid date format. Use DD/MM/YYYY (e.g., 15/03/2020).", "nextAction": "retry"}
                data["date_of_birth"] = dob
                s["state"] = STATES.BIRTH_SEX
                return {"response": lang["birth_sex"], "nextAction": "button_choice", "options": ["A", "B"]}

            if state == STATES.BIRTH_SEX:
                sex = data.get("sex")
                if not sex:
                    if cmd.choice and cmd.choice in ["A", "B"]:
                        sex = "Male" if cmd.choice == "A" else "Female"
                    elif msg.upper() == "A":
                        sex = "Male"
                    elif msg.upper() == "B":
                        sex = "Female"
                    else:
                        return {"response": lang["birth_sex"], "nextAction": "button_choice", "options": ["A", "B"]}
                data["sex"] = sex
                s["state"] = STATES.BIRTH_FATHER_NAME
                return {"response": lang["birth_father_name"], "nextAction": "input_field", "fieldType": "text"}

            if state == STATES.BIRTH_FATHER_NAME:
                father_name = data.get("father_name") or (msg if msg and not cmd.choice else None)
                if not father_name:
                    return {"response": lang["birth_father_name"], "nextAction": "input_field", "fieldType": "text"}
                data["father_name"] = father_name
                s["state"] = STATES.BIRTH_MOTHER_NAME
                return {"response": lang["birth_mother_name"], "nextAction": "input_field", "fieldType": "text"}

            if state == STATES.BIRTH_MOTHER_NAME:
                mother_name = data.get("mother_name") or (msg if msg and not cmd.choice else None)
                if not mother_name:
                    return {"response": lang["birth_mother_name"], "nextAction": "input_field", "fieldType": "text"}
                data["mother_name"] = mother_name
                s["state"] = STATES.BIRTH_DOCUMENTS
                return {"response": lang["birth_documents"], "nextAction": "file_upload", "fieldType": "file"}

            if state == STATES.BIRTH_PAYMENT:
                payment_choice = cmd.choice or msg.upper() if msg else None
                if payment_choice == "A":
                    ref = f"BIRTH/{datetime.now().year}/{self._gen_ref()}"
                    data["reference_number"] = ref
                    s["state"] = STATES.BIRTH_PRINT_OPTION
                    return {
                        "response": f"Dial *144#\nAmount: 100 ETB\nReference: {ref}\n\nReply 'DONE' after payment (or just continue for demo).",
                        "nextAction": "input_field",
                        "fieldType": "text",
                    }
                s["state"] = STATES.BIRTH_PRINT_OPTION
                return {"response": lang["birth_print_option"], "nextAction": "button_choice", "options": ["A", "B", "C"]}

            if state == STATES.BIRTH_PRINT_OPTION:
                print_choice = cmd.choice or msg.upper() if msg else None
                if not print_choice or print_choice not in ["A", "B", "C"]:
                    return {"response": lang["birth_print_option"], "nextAction": "button_choice", "options": ["A", "B", "C"]}
                
                ref = data.get("reference_number") or f"BIRTH/{datetime.now().year}/{self._gen_ref()}"
                data["reference_number"] = ref
                data["print_option"] = print_choice
                
                # Generate PDF
                pdf_path = None
                try:
                    ensure_generated_dir()
                    pdf_filename = f"{ref.replace('/', '_')}.pdf"
                    pdf_path = Path("data/generated") / pdf_filename
                    generate_birth_certificate_pdf(data, str(pdf_path))
                    data["pdf_path"] = str(pdf_path)
                except Exception as e:
                    print(f"Warning: PDF generation failed: {e}")
                    data["pdf_path"] = None
                
                s["state"] = STATES.BIRTH_COMPLETE
                response_msg = f"✅ Birth Certificate Request Complete!\n\nReference: {ref}\n\nProcessing time: ~15 minutes (demo)\nThank you!"
                if pdf_path:
                    response_msg += f"\n\n📄 Your PDF is ready for download below."
                
                return {
                    "response": response_msg,
                    "nextAction": "complete",
                    "data": data,
                    "pdf_path": str(pdf_path) if pdf_path else None,
                }

        # ---- ID appointment flow
        if service == "id_appointment":
            # Try auto-advance first
            auto_result = self._auto_advance_id_appointment(s, data, lang)
            if auto_result:
                return auto_result
            
            if state == STATES.ID_AGE:
                age = data.get("age")
                if not age:
                    age_str = msg if msg and not cmd.choice else None
                    if not age_str:
                        return {"response": lang["id_age"], "nextAction": "input_field", "fieldType": "number"}
                    try:
                        age = int(age_str)
                    except Exception:
                        return {"response": "Please enter a number (age).", "nextAction": "retry"}
                if age < 16:
                    return {"response": "You must be at least 16 years old. Enter your age again.", "nextAction": "retry"}
                data["age"] = age
                s["state"] = STATES.ID_HAS_ID
                return {"response": lang["id_has_id"], "nextAction": "button_choice", "options": ["A", "B"]}

            if state == STATES.ID_HAS_ID:
                has_id = data.get("has_previous_id")
                if has_id is None:
                    if cmd.choice:
                        has_id = (cmd.choice == "A")
                    elif msg.upper() == "A":
                        has_id = True
                    elif msg.upper() == "B":
                        has_id = False
                    else:
                        return {"response": lang["id_has_id"], "nextAction": "button_choice", "options": ["A", "B"]}
                data["has_previous_id"] = has_id
                s["state"] = STATES.ID_SLOT_SELECTION
                return {"response": lang["id_slot_selection"], "nextAction": "button_choice", "options": ["A", "B", "C", "D"]}

            if state == STATES.ID_SLOT_SELECTION:
                slot_choice = cmd.choice or msg.upper() if msg else None
                slot_map = {
                    "A": ("2025-12-27", "09:00"),
                    "B": ("2025-12-27", "10:00"),
                    "C": ("2025-12-28", "09:00"),
                    "D": ("2025-12-28", "10:00"),
                }
                if not slot_choice or slot_choice not in slot_map:
                    return {"response": lang["id_slot_selection"], "nextAction": "button_choice", "options": ["A", "B", "C", "D"]}
                data["appointment_date"], data["appointment_time"] = slot_map[slot_choice]
                s["state"] = STATES.ID_DOCUMENTS
                return {"response": lang["id_documents"], "nextAction": "input_field", "fieldType": "text"}

            if state == STATES.ID_DOCUMENTS:
                data["documents_note"] = msg if msg else "Documents noted"
                s["state"] = STATES.ID_PAYMENT
                return {"response": lang["id_payment_amount"], "nextAction": "button_choice", "options": ["A", "B"]}

            if state == STATES.ID_PAYMENT:
                ref = f"ID/{datetime.now().year}/{self._gen_ref()}"
                data["reference_number"] = ref
                s["state"] = STATES.ID_COMPLETE
                return {
                    "response": f"✅ Appointment booked!\n\nReference: {ref}\nDate: {data['appointment_date']}\nTime: {data['appointment_time']}\nLocation: Kebele Office (demo)\n",
                    "nextAction": "complete",
                    "data": data,
                }

        # If we get here and intent is unknown, provide helpful context
        if cmd.intent == "unknown":
            if state == STATES.GREETING:
                return {"response": lang["greeting"], "nextAction": "button_choice", "options": ["A", "B"]}
            # Provide context-aware response
            context_responses = {
                STATES.BIRTH_CHILD_NAME: lang["birth_child_name"],
                STATES.BIRTH_DOB: lang["birth_dob"],
                STATES.BIRTH_SEX: lang["birth_sex"],
                STATES.BIRTH_FATHER_NAME: lang["birth_father_name"],
                STATES.BIRTH_MOTHER_NAME: lang["birth_mother_name"],
                STATES.ID_AGE: lang["id_age"],
            }
            return {"response": context_responses.get(state, "Please provide the requested information."), "nextAction": "retry"}

        return {"response": "Sorry, I didn't understand. Please try again.", "nextAction": "retry"}


agent = KebeleAgent()
