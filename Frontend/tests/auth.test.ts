import {
  attemptLogout,
  attemptRegistration,
  authGuardMiddleware,
  authUserLoader,
  AuthState,
} from '../src/data/auth'
import Api from '../src/data/Api'
import { ResponseError } from '../src/api'
import {
  BEARER_AUTH_COOKIE,
  CURRENT_USER_ID_COOKIE,
  CURRENT_USER_IS_DEBUG_COOKIE,
  CURRENT_USER_NAME_COOKIE,
  CURRENT_USER_ORGANIZATION_COOKIE,
} from '../src/data/cookies'
import { beforeEach, describe, expect, test, vi, Mock } from 'vitest'

vi.mock('../src/data/Api', () => ({
  __esModule: true,
  default: {
    auth: {
      authLogoutPost: vi.fn(),
      authRegisterPost: vi.fn(),
    },
  },
}))

/* vi.mock('../src/data/Api.ts')

const mockedApi = vi.mocked(typeof Api) */

const mockedApi = vi.mocked(Api, true)

function createCookieStoreMock() {
  return {
    delete: vi.fn<(name: string) => Promise<void>>().mockResolvedValue(undefined),
    set: vi.fn<(value: unknown) => Promise<void>>().mockResolvedValue(undefined),
    get: vi.fn<(name: string) => Promise<{ value: string } | null>>().mockResolvedValue(null),
  }
}

describe('attemptLogout', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.defineProperty(globalThis, 'cookieStore', {
      value: createCookieStoreMock(),
      configurable: true,
    })
  })

  test('test_attempt_logout_deletes_all_auth_cookies_when_api_logout_fails', async () => {
    mockedApi.auth.authLogoutPost.mockRejectedValue(new Error('API error'))

    await attemptLogout()

    expect(cookieStore.delete).toHaveBeenCalledWith(BEARER_AUTH_COOKIE)
    expect(cookieStore.delete).toHaveBeenCalledWith(CURRENT_USER_ID_COOKIE)
    expect(cookieStore.delete).toHaveBeenCalledWith(CURRENT_USER_NAME_COOKIE)
    expect(cookieStore.delete).toHaveBeenCalledWith(CURRENT_USER_IS_DEBUG_COOKIE)
    expect(cookieStore.delete).toHaveBeenCalledWith(CURRENT_USER_ORGANIZATION_COOKIE)
  })
})

describe('attemptRegistration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('test_attempt_registration_returns_success_with_created_user_id', async () => {
    mockedApi.auth.authRegisterPost.mockResolvedValue({
      id: 'user-123',
    })

    const result = await attemptRegistration(
      'Jan',
      'Kowalski',
      'jkowalski',
      'jan@example.com',
      'secret-password'
    )

    expect(result).toEqual({
      success: true,
      id: 'user-123',
    })
  })

  test('test_attempt_registration_returns_username_or_email_taken_when_api_returns_409', async () => {
    mockedApi.auth.authRegisterPost.mockRejectedValue(
      new ResponseError(new Response(null, { status: 409 }), 'Conflict')
    )

    const result = await attemptRegistration(
      'Jan',
      'Kowalski',
      'jkowalski',
      'jan@example.com',
      'secret-password'
    )

    expect(result).toEqual({
      success: false,
      errorCause: 'username_or_email_taken',
    })
  })

  test('test_attempt_registration_returns_username_too_short_when_api_returns_422', async () => {
    mockedApi.auth.authRegisterPost.mockRejectedValue(
      new ResponseError(new Response(null, { status: 422 }), 'Validation error')
    )

    const result = await attemptRegistration(
      'Jan',
      'Kowalski',
      'jk',
      'jan@example.com',
      'secret-password'
    )

    expect(result).toEqual({
      success: false,
      errorCause: 'username_too_short',
    })
  })

  test('test_attempt_registration_returns_unknown_when_api_returns_unexpected_error', async () => {
    mockedApi.auth.authRegisterPost.mockRejectedValue(new Error('Network error'))

    const result = await attemptRegistration(
      'Jan',
      'Kowalski',
      'jkowalski',
      'jan@example.com',
      'secret-password'
    )

    expect(result).toEqual({
      success: false,
      errorCause: 'unknown',
    })
  })
})

describe('authGuardMiddleware', () => {
  test('test_auth_guard_redirects_to_login_when_auth_state_missing', async () => {
    const context = {
      get: vi.fn().mockReturnValue(null),
    }
    const next = vi.fn<() => Promise<unknown>>()

    await expect(authGuardMiddleware({ context } as never, next)).rejects.toThrow()

    expect(next).not.toHaveBeenCalled()
  })

  test('test_auth_guard_calls_next_when_auth_state_exists', async () => {
    const authState = new AuthState('jan', 'user-123', false)
    const context = {
      get: vi.fn().mockReturnValue(authState),
    }
    const next = vi.fn<() => Promise<unknown>>().mockResolvedValue('ok')

    const result = await authGuardMiddleware({ context } as never, next)

    expect(result).toBe('ok')
  })
})

describe('authUserLoader', () => {
  test('test_auth_user_loader_returns_auth_state_when_auth_state_exists', async () => {
    const authState = new AuthState('jan', 'user-123', false)
    const context = {
      get: vi.fn().mockReturnValue(authState),
    }

    const result = await authUserLoader({ context } as never)

    expect(result).toBe(authState)
  })

  test('test_auth_user_loader_redirects_to_login_when_auth_state_missing', async () => {
    const context = {
      get: vi.fn().mockReturnValue(null),
    }

    await expect(authUserLoader({ context } as never)).rejects.toThrow()
  })
})