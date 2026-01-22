/**
 * Authentication API response types.
 * These types match the backend TokenResponse schema.
 */

export interface UserResponse {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
}

export interface ClinicResponse {
    id: string;
    name: string;
    slug: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
    user: UserResponse;
    clinic: ClinicResponse;
}

export interface ErrorResponse {
    detail: string;
}
