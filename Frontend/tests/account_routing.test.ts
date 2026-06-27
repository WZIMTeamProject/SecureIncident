import { beforeEach, describe, expect, test, vi } from 'vitest'
import { accountAction } from '../src/account/routing.ts'
import Api from '../src/data/Api.ts'
import { ResponseError } from '../src/api/index.ts'
import {
  FORM_ACTION,
  FORM_ACTION_CHANGE_PASSWORD,
  FORM_ACTION_UPDATE_PROFILE,
  FORM_BIO,
  FORM_CURRENT_PW,
  FORM_NEW_PW,
  FORM_PICTURE_URL,
} from '../src/account/forms.ts'

vi.mock('../src/data/Api.ts', () => ({
  __esModule: true,
  default: {
    auth: {
      authChangePasswordPost: vi.fn().mockResolvedValue(undefined),
    },
    profiles: {
      profilesMePatch: vi.fn().mockResolvedValue(undefined),
    },
  },
}))

const mockedApi = vi.mocked(Api, true)

function createFormRequest(
  values: Record<string, string>,
  method = 'POST'
): Request {
  const formData = new FormData()

  Object.entries(values).forEach(([key, value]) => {
    formData.set(key, value)
  })

  return new Request('http://localhost/account', {
    method,
    body: formData,
  })
}

function createResponseError(status: number, detail?: string): ResponseError {
  return new ResponseError(
    new Response(
      detail === undefined ? null : JSON.stringify({ detail }),
      {
        status,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    ),
    'API error'
  )
}

describe('accountAction', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('test_account_action_returns_invalid_request_when_action_missing', async () => {
    const request = createFormRequest({})

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Nieprawidłowe żądanie.',
    })
  })

  test('test_account_action_returns_invalid_request_when_method_is_not_post', async () => {
    const request = createFormRequest(
      {
        [FORM_ACTION]: FORM_ACTION_UPDATE_PROFILE,
      },
      'PUT'
    )

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Nieprawidłowe żądanie.',
    })
  })

  test('test_account_action_returns_unknown_operation_when_action_is_not_supported', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: 'unsupported_action',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Nieznana operacja.',
    })
  })

  test('test_account_action_updates_profile_with_bio_and_picture_url', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_UPDATE_PROFILE,
      [FORM_BIO]: '  Security analyst  ',
      [FORM_PICTURE_URL]: '  https://example.com/avatar.png  ',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({ ok: true })
    expect(mockedApi.profiles.profilesMePatch).toHaveBeenCalledWith({
      updateProfileRequest: {
        bio: 'Security analyst',
        profilePictureUrl: 'https://example.com/avatar.png',
      },
    })
  })

  test('test_account_action_updates_profile_with_null_picture_url_when_url_is_empty', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_UPDATE_PROFILE,
      [FORM_BIO]: 'User bio',
      [FORM_PICTURE_URL]: '   ',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({ ok: true })
    expect(mockedApi.profiles.profilesMePatch).toHaveBeenCalledWith({
      updateProfileRequest: {
        bio: 'User bio',
        profilePictureUrl: null,
      },
    })
  })

  test('test_account_action_updates_profile_with_empty_bio_when_bio_missing', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_UPDATE_PROFILE,
      [FORM_PICTURE_URL]: 'https://example.com/avatar.png',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({ ok: true })
    expect(mockedApi.profiles.profilesMePatch).toHaveBeenCalledWith({
      updateProfileRequest: {
        bio: '',
        profilePictureUrl: 'https://example.com/avatar.png',
      },
    })
  })

  test('test_account_action_returns_profile_error_when_profile_update_fails', async () => {
    mockedApi.profiles.profilesMePatch.mockRejectedValue(new Error('API error'))

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_UPDATE_PROFILE,
      [FORM_BIO]: 'User bio',
      [FORM_PICTURE_URL]: 'https://example.com/avatar.png',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Nie udało się zapisać profilu.',
    })
  })

  test('test_account_action_returns_required_fields_error_when_current_password_missing', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_CHANGE_PASSWORD,
      [FORM_NEW_PW]: 'new-password',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Wszystkie pola są wymagane.',
    })
    expect(mockedApi.auth.authChangePasswordPost).not.toHaveBeenCalled()
  })

  test('test_account_action_returns_required_fields_error_when_new_password_missing', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_CHANGE_PASSWORD,
      [FORM_CURRENT_PW]: 'current-password',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Wszystkie pola są wymagane.',
    })
    expect(mockedApi.auth.authChangePasswordPost).not.toHaveBeenCalled()
  })

  test('test_account_action_changes_password_with_valid_data', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_CHANGE_PASSWORD,
      [FORM_CURRENT_PW]: 'current-password',
      [FORM_NEW_PW]: 'new-password',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({ ok: true })
    expect(mockedApi.auth.authChangePasswordPost).toHaveBeenCalledWith({
      changePasswordRequest: {
        currentPassword: 'current-password',
        newPassword: 'new-password',
      },
    })
  })

  test('test_account_action_returns_new_password_error_when_passwords_are_same', async () => {
    mockedApi.auth.authChangePasswordPost.mockRejectedValue(
      createResponseError(400, 'New password must be different from the current password')
    )

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_CHANGE_PASSWORD,
      [FORM_CURRENT_PW]: 'same-password',
      [FORM_NEW_PW]: 'same-password',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      field: 'new_password',
      error: 'Nowe hasło musi różnić się od obecnego.',
    })
  })

  test('test_account_action_returns_current_password_error_when_current_password_is_incorrect', async () => {
    mockedApi.auth.authChangePasswordPost.mockRejectedValue(
      createResponseError(400, 'Current password is incorrect')
    )

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_CHANGE_PASSWORD,
      [FORM_CURRENT_PW]: 'wrong-password',
      [FORM_NEW_PW]: 'new-password',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      field: 'current_password',
      error: 'Nieprawidłowe aktualne hasło.',
    })
  })

  test('test_account_action_returns_neutral_error_when_bad_request_detail_is_missing', async () => {
    mockedApi.auth.authChangePasswordPost.mockRejectedValue(
      createResponseError(400)
    )

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_CHANGE_PASSWORD,
      [FORM_CURRENT_PW]: 'current-password',
      [FORM_NEW_PW]: 'new-password',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Nie udało się zmienić hasła. Sprawdź wprowadzone dane.',
    })
  })

  test('test_account_action_returns_new_password_error_when_api_returns_422', async () => {
    mockedApi.auth.authChangePasswordPost.mockRejectedValue(
      createResponseError(422)
    )

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_CHANGE_PASSWORD,
      [FORM_CURRENT_PW]: 'current-password',
      [FORM_NEW_PW]: 'short',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      field: 'new_password',
      error: 'Nowe hasło jest zbyt słabe lub za krótkie.',
    })
  })

  test('test_account_action_returns_session_expired_error_when_api_returns_401', async () => {
    mockedApi.auth.authChangePasswordPost.mockRejectedValue(
      createResponseError(401)
    )

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_CHANGE_PASSWORD,
      [FORM_CURRENT_PW]: 'current-password',
      [FORM_NEW_PW]: 'new-password',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Sesja wygasła. Zaloguj się ponownie.',
    })
  })

  test('test_account_action_returns_generic_password_error_when_api_returns_500', async () => {
    mockedApi.auth.authChangePasswordPost.mockRejectedValue(
      createResponseError(500)
    )

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_CHANGE_PASSWORD,
      [FORM_CURRENT_PW]: 'current-password',
      [FORM_NEW_PW]: 'new-password',
    })

    const result = await accountAction({ request } as never)

    expect(result).toEqual({
      ok: false,
      error: 'Nie udało się zmienić hasła.',
    })
  })
})