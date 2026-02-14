const JSON_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
};

function authHeaders(token) {
    return {
        ...JSON_HEADERS,
        Authorization: token,
    };
}

async function handleResponse(res) {
    const data = await res.json();
    if (!res.ok) {
        const error = new Error(data.message || res.statusText);
        error.status = res.status;
        error.data = data;
        throw error;
    }
    return data;
}

// Auth

export async function createUser(email, password) {
    const res = await fetch('/api/create_user', {
        method: 'POST',
        headers: JSON_HEADERS,
        body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
}

export async function getToken(email, password) {
    const res = await fetch('/api/get_token', {
        method: 'POST',
        headers: JSON_HEADERS,
        body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
}

export async function isTokenValid(token) {
    const res = await fetch('/api/is_token_valid', {
        method: 'POST',
        headers: JSON_HEADERS,
        body: JSON.stringify({ token }),
    });
    return handleResponse(res);
}

// User data

export async function getUserData(token) {
    const res = await fetch('/api/user', {
        headers: authHeaders(token),
    });
    return handleResponse(res);
}

// Stock data

export async function getStrategies() {
    const res = await fetch('/api/strategies');
    return handleResponse(res);
}

export async function getRankings(strategy) {
    const res = await fetch(`/api/rankings/${strategy}`);
    return handleResponse(res);
}

export async function getCompanies() {
    const res = await fetch('/api/companies');
    return handleResponse(res);
}

export async function getCompany(symbol) {
    const res = await fetch(`/api/companies/${symbol}`);
    return handleResponse(res);
}

export async function getHealth() {
    const res = await fetch('/api/health');
    return handleResponse(res);
}
