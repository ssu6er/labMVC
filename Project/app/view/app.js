const TOKEN_KEY = "random_choice_token";

const authSection = document.getElementById("auth-section");
const appSection = document.getElementById("app-section");
const userPanel = document.getElementById("user-panel");
const currentUserName = document.getElementById("current-user-name");
const messageBox = document.getElementById("message");
const categoriesList = document.getElementById("categories-list");
const optionsCard = document.getElementById("options-card");
const optionsList = document.getElementById("options-list");
const historyList = document.getElementById("history-list");
const selectedCategoryName = document.getElementById("selected-category-name");
const resultBox = document.getElementById("result-box");
const resultTitle = document.getElementById("result-title");

let categories = [];
let currentCategory = null;

function showMessage(text, type = "error") {
    messageBox.textContent = text;
    messageBox.classList.toggle("success", type === "success");
    messageBox.classList.remove("hidden");
}

function clearMessage() {
    messageBox.textContent = "";
    messageBox.classList.add("hidden");
    messageBox.classList.remove("success");
}

function errorText(data, fallback) {
    if (!data) return fallback;
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
        return data.detail.map((item) => item.msg || "Nieprawidłowe dane").join(". ");
    }
    return fallback;
}

async function api(path, options = {}) {
    const headers = new Headers(options.headers || {});
    const token = localStorage.getItem(TOKEN_KEY);

    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (options.body && !(options.body instanceof FormData)) {
        headers.set("Content-Type", "application/json");
    }

    let response;
    try {
        response = await fetch(path, { ...options, headers });
    } catch (_) {
        throw new Error("Nie udało się połączyć z serwerem");
    }

    const hasJson = response.headers.get("content-type")?.includes("application/json");
    const data = response.status === 204 ? null : hasJson ? await response.json() : null;

    if (response.status === 401) {
        localStorage.removeItem(TOKEN_KEY);
        showAuth();
    }

    if (!response.ok) {
        throw new Error(errorText(data, `Błąd żądania: ${response.status}`));
    }

    return data;
}

function showAuth() {
    authSection.classList.remove("hidden");
    appSection.classList.add("hidden");
    userPanel.classList.add("hidden");
    currentCategory = null;
    optionsCard.classList.add("hidden");
}

function showApp(user) {
    authSection.classList.add("hidden");
    appSection.classList.remove("hidden");
    userPanel.classList.remove("hidden");
    currentUserName.textContent = user.name;
}

function createButton(text, className, handler) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `button button-small ${className}`.trim();
    button.textContent = text;
    button.addEventListener("click", handler);
    return button;
}

function emptyState(text) {
    const element = document.createElement("div");
    element.className = "empty-state";
    element.textContent = text;
    return element;
}

function renderCategories() {
    categoriesList.replaceChildren();

    if (!categories.length) {
        categoriesList.append(emptyState("Nie masz jeszcze żadnych kategorii"));
        return;
    }

    for (const category of categories) {
        const row = document.createElement("div");
        row.className = "item-row";

        const title = document.createElement("span");
        title.className = "item-title";
        title.textContent = category.name;

        const actions = document.createElement("div");
        actions.className = "item-actions";
        actions.append(
            createButton("Otwórz", "", () => openCategory(category)),
            createButton("Usuń", "button-danger", () => removeCategory(category))
        );

        row.append(title, actions);
        categoriesList.append(row);
    }
}

async function loadCategories() {
    categories = await api("/api/categories");
    renderCategories();

    if (currentCategory) {
        const updated = categories.find((item) => item.id === currentCategory.id);
        if (!updated) {
            currentCategory = null;
            optionsCard.classList.add("hidden");
        }
    }
}

async function openCategory(category) {
    clearMessage();
    currentCategory = category;
    selectedCategoryName.textContent = category.name;
    resultBox.classList.add("hidden");
    optionsCard.classList.remove("hidden");
    await loadOptions();
    optionsCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function removeCategory(category) {
    if (!confirm(`Usunąć kategorię „${category.name}”?`)) return;

    try {
        await api(`/api/categories/${category.id}`, { method: "DELETE" });
        if (currentCategory?.id === category.id) {
            currentCategory = null;
            optionsCard.classList.add("hidden");
        }
        await Promise.all([loadCategories(), loadHistory()]);
        showMessage("Kategoria została usunięta", "success");
    } catch (error) {
        showMessage(error.message);
    }
}

function renderOptions(options) {
    optionsList.replaceChildren();

    if (!options.length) {
        optionsList.append(emptyState("Dodaj pierwszą opcję"));
        return;
    }

    for (const option of options) {
        const row = document.createElement("div");
        row.className = "item-row";

        const main = document.createElement("div");
        main.className = "item-main";

        const status = document.createElement("span");
        status.className = `status${option.is_active ? "" : " inactive"}`;
        status.textContent = option.is_active ? "Aktywna" : "Nieaktywna";

        const title = document.createElement("span");
        title.className = "item-title";
        title.textContent = option.title;
        main.append(status, title);

        const actions = document.createElement("div");
        actions.className = "item-actions";
        actions.append(
            createButton(option.is_active ? "Wyłącz" : "Włącz", "button-secondary", () => toggleOption(option.id)),
            createButton("Usuń", "button-danger", () => removeOption(option.id))
        );

        row.append(main, actions);
        optionsList.append(row);
    }
}

async function loadOptions() {
    if (!currentCategory) return;
    const options = await api(`/api/categories/${currentCategory.id}/options`);
    renderOptions(options);
}

async function toggleOption(optionId) {
    try {
        await api(`/api/options/${optionId}/toggle`, { method: "PATCH" });
        await loadOptions();
    } catch (error) {
        showMessage(error.message);
    }
}

async function removeOption(optionId) {
    if (!confirm("Usunąć tę opcję?")) return;

    try {
        await api(`/api/options/${optionId}`, { method: "DELETE" });
        await loadOptions();
    } catch (error) {
        showMessage(error.message);
    }
}

function renderHistory(items) {
    historyList.replaceChildren();
    document.getElementById("clear-history-button").disabled = items.length === 0;

    if (!items.length) {
        historyList.append(emptyState("Historia jest pusta"));
        return;
    }

    for (const item of items) {
        const row = document.createElement("div");
        row.className = "history-row";

        const title = document.createElement("strong");
        title.textContent = item.selected_option_title;

        const time = document.createElement("time");
        time.dateTime = item.created_at;
        time.textContent = new Date(item.created_at).toLocaleString("pl-PL");

        row.append(title, time);
        historyList.append(row);
    }
}

async function loadHistory() {
    renderHistory(await api("/api/history"));
}

document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage();

    try {
        const data = await api("/api/login", {
            method: "POST",
            body: JSON.stringify({
                email: document.getElementById("login-email").value,
                password: document.getElementById("login-password").value
            })
        });
        localStorage.setItem(TOKEN_KEY, data.access_token);
        document.getElementById("login-password").value = "";
        await initializeApp();
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById("register-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage();

    const email = document.getElementById("register-email").value;
    try {
        await api("/api/register", {
            method: "POST",
            body: JSON.stringify({
                name: document.getElementById("register-name").value,
                email,
                password: document.getElementById("register-password").value
            })
        });
        event.target.reset();
        document.getElementById("login-email").value = email;
        showMessage("Rejestracja zakończona pomyślnie. Teraz możesz się zalogować.", "success");
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById("logout-button").addEventListener("click", () => {
    localStorage.removeItem(TOKEN_KEY);
    clearMessage();
    showAuth();
});

document.getElementById("category-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage();
    const input = document.getElementById("category-name");

    try {
        await api("/api/categories", {
            method: "POST",
            body: JSON.stringify({ name: input.value })
        });
        input.value = "";
        await loadCategories();
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById("option-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!currentCategory) return;
    clearMessage();
    const input = document.getElementById("option-title");

    try {
        await api(`/api/categories/${currentCategory.id}/options`, {
            method: "POST",
            body: JSON.stringify({ title: input.value })
        });
        input.value = "";
        await loadOptions();
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById("random-button").addEventListener("click", async () => {
    if (!currentCategory) return;
    clearMessage();

    try {
        const result = await api(`/api/categories/${currentCategory.id}/random`, { method: "POST" });
        resultTitle.textContent = result.selected_option_title;
        resultBox.classList.remove("hidden", "result-visible");
        void resultBox.offsetWidth;
        resultBox.classList.add("result-visible");
        await loadHistory();
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById("clear-history-button").addEventListener("click", async () => {
    if (!confirm("Wyczyścić całą historię?")) return;

    try {
        await api("/api/history", { method: "DELETE" });
        await loadHistory();
        showMessage("Historia została wyczyszczona", "success");
    } catch (error) {
        showMessage(error.message);
    }
});

async function initializeApp() {
    try {
        const user = await api("/api/me");
        showApp(user);
        clearMessage();
        await Promise.all([loadCategories(), loadHistory()]);
    } catch (error) {
        if (localStorage.getItem(TOKEN_KEY)) showMessage(error.message);
        showAuth();
    }
}

if (localStorage.getItem(TOKEN_KEY)) {
    initializeApp();
} else {
    showAuth();
}
