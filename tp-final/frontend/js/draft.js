import { storageGet, storageSet } from "./ui.js";

// Borrador de la sesión en curso: sobrevive a un corte de señal o a cerrar la pestaña.
const KEY = "gymbro.draft";

export function loadDraft() {
  return storageGet(KEY);
}

export function saveDraft(draft) {
  storageSet(KEY, draft);
}

export function clearDraft() {
  storageSet(KEY, null);
}

export function newDraft({ code, date, bodyweight, plan = [], routineDayId = null, title = "Carga libre" }) {
  return { code, date, bodyweight, plan, routineDayId, title, step: 0, sets: [], exerciseId: plan[0]?.exercise_id ?? null };
}

/** Cuántas series lleva el ejercicio actual en este borrador. */
export function setsDone(draft, exerciseId) {
  return draft.sets.filter((s) => s.exercise_id === exerciseId).length;
}
