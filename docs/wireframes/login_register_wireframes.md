# Login and Registration Wireframes

This document provides wireframe designs for the login and registration screens.
The goal is to replace the minimal forms in `Login.jsx` and `Register.jsx` with a
more polished UI that reflects LinChat's brand and works well on mobile and
desktop.

## Design Goals

1. **Responsive layout** – forms should adapt to phone, tablet and desktop.
2. **Clear error handling** – show field-specific errors inline.
3. **Brand styling** – use the primary color and typography from `theme.js`.

Both screens use a centered form card with a logo at the top.

---

## Login Form Wireframe

```
+-----------------------------------------------------+
| [LinChat logo]                                      |
|                                                     |
|             +----------------------------+          |
|             | Login to LinChat          |          |
|             +----------------------------+          |
|                                                     |
|  [Username    _______________________ ] (error)     |
|  [Password    _______________________ ] (error)     |
|                                                     |
|            (Login button - primary color)           |
|                                                     |
|    [Forgot password?]    [Create an account]        |
+-----------------------------------------------------+
```

### Notes
- Form sits inside a max 400px wide card with padding.
- Errors appear in red text below each input.
- The login button spans full width on mobile, 50% on desktop.
- Links below the button navigate to recovery/registration.

---

## Registration Form Wireframe

```
+-----------------------------------------------------+
| [LinChat logo]                                      |
|                                                     |
|             +----------------------------+          |
|             | Create an Account         |          |
|             +----------------------------+          |
|                                                     |
|  [Username    _______________________ ] (error)     |
|  [Email       _______________________ ] (error)     |
|  [Password    _______________________ ] (error)     |
|                                                     |
|           (Register button - primary color)         |
|                                                     |
|         [Already have an account? Login]            |
+-----------------------------------------------------+
```

### Notes
- Same centered card and responsive layout as the login form.
- Each field shows inline errors.
- After successful registration, redirect to the login page.

---

## Styling Recommendations

- Import LinChat logo and place it above the form heading.
- Use the MUI `Container` component to center the card and provide responsive
  spacing.
- Set `maxWidth="sm"` on the container to limit width on large screens.
- Colors and fonts come from `theme.js` – customize `primary.main` to the brand
  color and `typography.fontFamily` to match LinChat's style.
- For errors, use MUI's built-in `error` prop on `TextField` and a helper text
  element for the message.

These wireframes serve as a foundation for implementing a more user-friendly and
branded authentication flow.
