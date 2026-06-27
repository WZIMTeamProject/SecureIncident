import { beforeEach, describe, expect, test, vi } from 'vitest'
import {
  forgotPasswordAction,
  loginFormAction,
  logoutMiddleware,
  redirectToDashboardMiddleware,
  registerFormAction,
  resetPasswordAction,
} from '../src/login/routing.ts'
import {
  attemptLogin,
  attemptLogout,
  attemptRegistration,
  AuthRouterContext,
  AuthState,
} from '../src/data/auth.ts'
import Api from '../src/data/Api.ts'
import {
  FORM_AFTER,
  FORM_EMAIL,
  FORM_FIRST_NAME,
  FORM_LAST_NAME,
  FORM_LOGOUT,
  FORM_PASSWORD,
  FORM_PASSWORD_REPEAT,
  FORM_REMEMBER_ME,
  FORM_RESET_TOKEN,
  FORM_USERNAME,
  FORM_VALUE_AFTER_PASSWORD_RESET,
  FORM_VALUE_AFTER_REGISTER,
} from '../src/login/forms.ts'
import * as validation from '../src/login/validation.ts'
import { validateName } from '../src/login/validation.ts'

vi.mock('../src/data/auth.ts', async () => {
  const actual = await vi.importActual<typeof import('../src/data/auth.ts')>(
    '../src/data/auth.ts'
  )

  return {
    ...actual,
    attemptLogin: vi.fn(),
    attemptLogout: vi.fn(),
    attemptRegistration: vi.fn(),
  }
})

vi.mock('../src/data/Api.ts', () => ({
  __esModule: true,
  default: {
    auth: {
      authRequestPasswordResetPost: vi.fn(),
      authResetPasswordPost: vi.fn(),
    },
  },
}))

vi.mock('../src/login/validation.ts', () => ({
  validateName: vi.fn(),
}))

const mockedAttemptLogin = vi.mocked(attemptLogin)
const mockedAttemptLogout = vi.mocked(attemptLogout)
const mockedAttemptRegistration = vi.mocked(attemptRegistration)
const mockedValidateName = vi.mocked(validateName)
const mockedApi = vi.mocked(Api, true)

function createFormRequest(values: Record<string, string>): Request {
  const formData = new FormData()

  Object.entries(values).forEach(([key, value]) => {
    formData.set(key, value)
  })

  return new Request('http://localhost/test', {
    method: 'POST',
    body: formData,
  })
}

function createRequest(url: string): Request {
  return new Request(url)
}

function createRouterContext(authState: AuthState | null = null) {
  return {
    get: vi.fn().mockImplementation((context) => {
      if (context === AuthRouterContext) {
        return authState
      }

      return null
    }),
    set: vi.fn(),
  }
}

describe('redirectToDashboardMiddleware', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('test_redirect_to_dashboard_redirects_when_auth_state_exists', async () => {
    const authState = new AuthState('jan', 'user-123', false)
    const context = createRouterContext(authState)
    const next = vi.fn<() => Promise<unknown>>().mockResolvedValue('ok')

    await expect(
      redirectToDashboardMiddleware({ context } as never, next)
    ).rejects.toThrow()

    expect(next).not.toHaveBeenCalled()
  })

  test('test_redirect_to_dashboard_calls_next_when_auth_state_missing', async () => {
    const context = createRouterContext(null)
    const next = vi.fn<() => Promise<unknown>>().mockResolvedValue('ok')

    const result = await redirectToDashboardMiddleware({ context } as never, next)

    expect(result).toBe('ok')
  })
})

describe('logoutMiddleware', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('test_logout_middleware_logs_out_when_logout_param_exists', async () => {
    const context = createRouterContext(new AuthState('jan', 'user-123', false))
    const request = createRequest(`http://localhost/login?${FORM_LOGOUT}=1`)
    const next = vi.fn<() => Promise<unknown>>().mockResolvedValue('ok')

    const result = await logoutMiddleware({ request, context } as never, next)

    expect(result).toBe('ok')
    expect(mockedAttemptLogout).toHaveBeenCalled()
    expect(context.set).toHaveBeenCalledWith(AuthRouterContext, null)
  })

  test('test_logout_middleware_does_not_log_out_when_logout_param_missing', async () => {
    const context = createRouterContext(new AuthState('jan', 'user-123', false))
    const request = createRequest('http://localhost/login')
    const next = vi.fn<() => Promise<unknown>>().mockResolvedValue('ok')

    const result = await logoutMiddleware({ request, context } as never, next)

    expect(result).toBe('ok')
    expect(mockedAttemptLogout).not.toHaveBeenCalled()
    expect(context.set).not.toHaveBeenCalled()
  })
})

describe('loginFormAction', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('test_login_form_returns_invalid_data_when_login_missing', async () => {
    const request = createFormRequest({
      [FORM_PASSWORD]: 'secret-password',
    })

    const result = await loginFormAction({ request } as never)

    expect(result).toEqual({ error: 'invalid_data' })
  })

  test('test_login_form_returns_invalid_credentials_when_login_fails', async () => {
    mockedAttemptLogin.mockResolvedValue(false)

    const request = createFormRequest({
      [FORM_USERNAME]: 'jan',
      [FORM_PASSWORD]: 'wrong-password',
    })

    const result = await loginFormAction({ request } as never)

    expect(result).toEqual({ error: 'invalid_credentials' })
  })

  test('test_login_form_redirects_to_dashboard_when_login_succeeds', async () => {
    mockedAttemptLogin.mockResolvedValue(true)

    const request = createFormRequest({
      [FORM_USERNAME]: 'jan',
      [FORM_PASSWORD]: 'secret-password',
      [FORM_REMEMBER_ME]: 'on',
    })

    const result = await loginFormAction({ request } as never)

    expect(result).toBeInstanceOf(Response)
    expect((result as Response).headers.get('Location')).toBe('/dashboard')
  })
})

describe('registerFormAction', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedValidateName.mockReturnValue(true)
  })

  test('test_register_form_returns_invalid_data_when_required_field_missing', async () => {
    const request = createFormRequest({
      [FORM_FIRST_NAME]: 'Jan',
      [FORM_LAST_NAME]: 'Kowalski',
      [FORM_USERNAME]: 'jkowalski',
      [FORM_PASSWORD]: 'secret-password',
    })

    const result = await registerFormAction({ request } as never)

    expect(result).toEqual({ error: 'invalid_data' })
  })

  test('test_register_form_returns_repeat_password_mismatch_when_passwords_differ', async () => {
    const request = createFormRequest({
      [FORM_FIRST_NAME]: 'Jan',
      [FORM_LAST_NAME]: 'Kowalski',
      [FORM_USERNAME]: 'jkowalski',
      [FORM_EMAIL]: 'jan@example.com',
      [FORM_PASSWORD]: 'secret-password',
      [FORM_PASSWORD_REPEAT]: 'different-password',
    })

    const result = await registerFormAction({ request } as never)

    expect(result).toEqual({ error: 'repeat_password_mismatch' })
  })

  test('test_register_form_returns_invalid_data_when_name_validation_fails', async () => {
    mockedValidateName.mockReturnValue(false)

    const request = createFormRequest({
      [FORM_FIRST_NAME]: 'Jan',
      [FORM_LAST_NAME]: 'Kowalski',
      [FORM_USERNAME]: 'jkowalski',
      [FORM_EMAIL]: 'jan@example.com',
      [FORM_PASSWORD]: 'secret-password',
      [FORM_PASSWORD_REPEAT]: 'secret-password',
    })

    const result = await registerFormAction({ request } as never)

    expect(result).toEqual({ error: 'invalid_data' })
  })

  test('test_register_form_redirects_to_login_after_successful_registration', async () => {
    mockedAttemptRegistration.mockResolvedValue({
      success: true,
      id: 'user-123',
    })

    const request = createFormRequest({
      [FORM_FIRST_NAME]: 'Jan',
      [FORM_LAST_NAME]: 'Kowalski',
      [FORM_USERNAME]: 'jkowalski',
      [FORM_EMAIL]: 'jan@example.com',
      [FORM_PASSWORD]: 'secret-password',
      [FORM_PASSWORD_REPEAT]: 'secret-password',
    })

    const result = await registerFormAction({ request } as never)

    expect(result).toBeInstanceOf(Response)
    expect((result as Response).headers.get('Location')).toBe(
      `/login?${FORM_AFTER}=${FORM_VALUE_AFTER_REGISTER}`
    )
  })

  test('test_register_form_returns_username_taken_when_username_or_email_is_taken', async () => {
    mockedAttemptRegistration.mockResolvedValue({
      success: false,
      errorCause: 'username_or_email_taken',
    })

    const request = createFormRequest({
      [FORM_FIRST_NAME]: 'Jan',
      [FORM_LAST_NAME]: 'Kowalski',
      [FORM_USERNAME]: 'jkowalski',
      [FORM_EMAIL]: 'jan@example.com',
      [FORM_PASSWORD]: 'secret-password',
      [FORM_PASSWORD_REPEAT]: 'secret-password',
    })

    const result = await registerFormAction({ request } as never)

    expect(result).toEqual({ error: 'username_taken' })
  })

  test('test_register_form_returns_username_too_short_when_api_reports_short_username', async () => {
    mockedAttemptRegistration.mockResolvedValue({
      success: false,
      errorCause: 'username_too_short',
    })

    const request = createFormRequest({
      [FORM_FIRST_NAME]: 'Jan',
      [FORM_LAST_NAME]: 'Kowalski',
      [FORM_USERNAME]: 'jk',
      [FORM_EMAIL]: 'jan@example.com',
      [FORM_PASSWORD]: 'secret-password',
      [FORM_PASSWORD_REPEAT]: 'secret-password',
    })

    const result = await registerFormAction({ request } as never)

    expect(result).toEqual({ error: 'username_too_short' })
  })
})

describe('forgotPasswordAction', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('test_forgot_password_returns_error_when_username_missing', async () => {
    const request = createFormRequest({})

    const result = await forgotPasswordAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Podaj e-mail lub nazwę użytkownika.',
    })
  })

  test('test_forgot_password_returns_ok_when_api_request_succeeds', async () => {
    mockedApi.auth.authRequestPasswordResetPost.mockResolvedValue(undefined)

    const request = createFormRequest({
      [FORM_USERNAME]: 'jan@example.com',
    })

    const result = await forgotPasswordAction({ request } as never)

    expect(result).toEqual({ ok: true })
  })

  test('test_forgot_password_returns_error_when_api_request_fails', async () => {
    mockedApi.auth.authRequestPasswordResetPost.mockRejectedValue(new Error('API error'))

    const request = createFormRequest({
      [FORM_USERNAME]: 'jan@example.com',
    })

    const result = await forgotPasswordAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Nie udało się wysłać żądania. Spróbuj ponownie później.',
    })
  })
})

describe('resetPasswordAction', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('test_reset_password_returns_invalid_data_when_token_missing', async () => {
    const request = createFormRequest({
      [FORM_PASSWORD]: 'secret-password',
      [FORM_PASSWORD_REPEAT]: 'secret-password',
    })

    const result = await resetPasswordAction({ request } as never)

    expect(result).toEqual({ error: 'invalid_data' })
  })

  test('test_reset_password_returns_repeat_password_mismatch_when_passwords_differ', async () => {
    const request = createFormRequest({
      [FORM_PASSWORD]: 'secret-password',
      [FORM_PASSWORD_REPEAT]: 'different-password',
      [FORM_RESET_TOKEN]: 'reset-token-123',
    })

    const result = await resetPasswordAction({ request } as never)

    expect(result).toEqual({ error: 'repeat_password_mismatch' })
  })

  test('test_reset_password_returns_invalid_token_when_api_request_fails', async () => {
    mockedApi.auth.authResetPasswordPost.mockRejectedValue(new Error('API error'))

    const request = createFormRequest({
      [FORM_PASSWORD]: 'secret-password',
      [FORM_PASSWORD_REPEAT]: 'secret-password',
      [FORM_RESET_TOKEN]: 'invalid-token',
    })

    const result = await resetPasswordAction({ request } as never)

    expect(result).toEqual({ error: 'invalid_token' })
  })

  test('test_reset_password_redirects_to_login_after_successful_password_reset', async () => {
    mockedApi.auth.authResetPasswordPost.mockResolvedValue(undefined)

    const request = createFormRequest({
      [FORM_PASSWORD]: 'secret-password',
      [FORM_PASSWORD_REPEAT]: 'secret-password',
      [FORM_RESET_TOKEN]: 'reset-token-123',
    })

    const result = await resetPasswordAction({ request } as never)

    expect(result).toBeInstanceOf(Response)
    expect((result as Response).headers.get('Location')).toBe(
      `/login?${FORM_AFTER}=${FORM_VALUE_AFTER_PASSWORD_RESET}`
    )
  })
})