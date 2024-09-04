
// <legal>
// 'Redemption' Automated Code Repair Tool
//
// Copyright 2023, 2024 Carnegie Mellon University.
//
// NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
// INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
// UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
// AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
// PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
// THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
// KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
// INFRINGEMENT.
//
// Licensed under a MIT (SEI)-style license, please see License.txt or
// contact permission@sei.cmu.edu for full terms.
//
// [DISTRIBUTION STATEMENT A] This material has been approved for public
// release and unlimited distribution.  Please see Copyright notice for
// non-US Government use and distribution.
//
// This Software includes and/or makes use of Third-Party Software each
// subject to its own license.
//
// DM23-2165
// </legal>

#if __STDC_VERSION__ >= 202311L
#  define ACR_NORETURN [[noreturn]]
#elif __STDC_VERSION__ >= 201112L
#  define ACR_NORETURN _Noreturn
#else
#  define ACR_NORETURN
#endif

int printf(const char *restrict format, ...);
ACR_NORETURN void abort(void);

// Note: `__typeof__` is a GCC/Clang extension; change `__typeof__` to `typeof`
// for C23-compliant compilers that don't recognize `__typeof__`.
// This file also uses the GCC "statement-expr" extension; see
// https://gcc.gnu.org/onlinedocs/gcc/Statement-Exprs.html


// If p_expr is NULL, execute '...', then abort.  Returns p_expr.
//
// null_check() works when p_expr is any expression, but fails if its
// result is used as an lvalue.  Example: null_check(x)++ fails.
#define null_check(p_expr, ...)                                         \
  ({ __typeof__(&*p_expr) _sei_acr_temp_bc_p = (p_expr);                \
    if (!_sei_acr_temp_bc_p) {                                          \
      __VA_ARGS__;                                                      \
      printf("Exiting due to detected impending null pointer dereference in file %s, function %s, line %d\n", __FILE__, __func__, __LINE__); \
      abort();                                                          \
    };                                                                  \
    _sei_acr_temp_bc_p;                                                 \
  })


// This version is the same, as null_check(), but requires p_expr to
// be an lvalue, and returns an lvalue.  This version will fail if
// p_expr results in a value that does not have an address.  Example:
// null_check_lval(x + 1) fails.
#define null_check_lval(p_expr, ...)                                    \
  (*({ __typeof__(&*p_expr) *_sei_acr_temp_bc_p = &(p_expr);            \
      if (!*_sei_acr_temp_bc_p) {                                       \
        __VA_ARGS__;                                                    \
        printf("Exiting due to detected impending null pointer dereference in file %s, function %s, line %d\n", __FILE__, __func__, __LINE__); \
        abort();                                                        \
      };                                                                \
      _sei_acr_temp_bc_p;                                               \
    }))
