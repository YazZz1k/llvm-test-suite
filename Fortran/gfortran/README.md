## Tests from the gfortran test suite ##

This is the top-level directory for tests imported from
[GCC](https://github.com/gcc-mirror/gcc). The test files are contained within
two subdirectories:

- `regression`: Contains the gfortran [tests](https://github.com/gcc-mirror/gcc/tree/master/gcc/testsuite/gfortran.dg).
- `torture`: Contains the gfortran [torture tests](https://github.com/gcc-mirror/gcc/tree/master/gcc/testsuite/gfortran.fortran-torture).

The tests in both `regression` (and its subdirectories) and `torture` can be
classified roughly as _compile_ tests and _execute_ tests. The _compile_ tests
generally check the compiler's error/warning messages and, in some cases,
optimization logs. The _execute_ tests are end-to-end tests that check the
behavior of the binary produced by the compiler.

Currently, only the _execute_ tests are supported in `regression`. Both
`compile` and `execute` tests have been enabled in `torture`.

Of the supported tests, a number of tests have been disabled. There are four
categories of such tests:

- *Unsupported*: These are tests that use non-standard extensions/intrinsics
that are not currently supported by flang. Unless those non-standard
features are supported in the future, these tests will never be enabled.

- *Unimplemented*: These tests hit a "not yet implemented" assertion within
flang.

- *Skipped*: These tests cause some form of compiler error. Some trigger an
assertion within the compiler. Others are legal Fortran programs, but
nevertheless cause a semantic error, most likely due to unimplemented
features.

- *Failing*: These tests fail at test-time.

  - For "execute" tests, some crash on execution, others produce
  incorrect/unexpected output. This could be a result of a bug in the
  compiler/code generator or the runtime.

  - For "compile" tests, this could be because the compilation succeeds when it
  is expected to fail, or vice versa.

Over time, the number of tests in the *unimplemented*, *skipped*, and *failing*
categories should decrease. Eventually, only the *unsupported* category should
remain.


### _Compile_ tests ###

The _compile_ tests are "built" when the whole test suite is built at which
time a compilation log is saved. At testing time, the log is checked to
determine whether the test should pass or fail. If the test is expected to pass,
but the compilation log contains errors, the test will be deemed to have failed
and vice versa. The _compile_ test are supported in `torture`, but not in
`regression`.


### _Execute tests_ ###

The _execute_ tests are built when the whole test suite is built and executed
when the tests are run. The *unsupported*, *unimplemented*, and *skipped* tests
fail to build for the reasons described above. The *failing* tests do build.


### Usage ###

By default, the *unsupported*, *unimplemented*, *skipped*, and *failing* tests
are not run. The intention is that all tests in the test suite should pass by
default.

In order to enable the disabled tests, one or more of the following options can
be passed to `cmake`:

- `TEST_SUITE_FORTRAN_FORCE_ALL_TESTS`: Enable all disabled tests.
- `TEST_SUITE_FORTRAN_FORCE_UNSUPPORTED_TESTS`: Enable only the *unsupported* tests.
- `TEST_SUITE_FORTRAN_FORCE_UNIMPLEMENTED_TESTS`: Enable only the *unimplemented* tests.
- `TEST_SUITE_FORTRAN_FORCE_SKIPPED_TESTS`: Enable only the *skipped* tests.
- `TEST_SUITE_FORTRAN_FORCE_FAILING_TESTS`: Enable only the *failing* tests.

Some of the tests require the `ISO_Fortran_binding.h` header file. `cmake` will
look for this file in the `include` directory of the `flang` installation
prefix. When running the test from a build directory, the file will probably
not be found. In that case, the `TEST_SUITE_FORTRAN_ISO_C_HEADER_DIR` flag
can be passed to `cmake` with the value being the directory containing the
`ISO_Fortran_binding.h` file to use.

A `cmake` command that would only run the Fortran tests in the test-suite is
shown below

```
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_C_COMPILER=/path/to/clang \
      -DCMAKE_CXX_COMPILER=/path/to/clang++ \
      -DCMAKE_Fortran_COMPILER=/path/to/flang-new \
      -DTEST_SUITE_FORTRAN=On \
      -DTEST_SUITE_SUBDIRS=Fortran \
      -DTEST_SUITE_FORTRAN_ISO_C_HEADER_DIR=/path/to/dir/containing/header \
      /path/to/source/of/llvm-test-suite/
```

The tests can be run as shown from the `llvm-test-suite` build directory:

```
/path/to/llvm-lit -v -o report.json .
```

It may be necessary to set the `NO_STOP_MESSAGE` environment variable to
avoid tests failures in `llvm-test-suite/Fortran/UnitTests/fcvs21_f95`. These
are unrelated to the gfortran tests here.


### Notes for developers/maintainers ###

Since `flang` is under active development, it is expected that features will be
implemented at a steady pace. The relevant tests in this directory should be
enabled. This would involve building the test suite with one of the
`TEST_SUITE_FORTRAN_*` flags described above.

The test files should be kept in sync with gfortran. This needs to be done
manually periodically.

The test files in `regression` and `torture` *must not* be modified.


### TODO's ###

If some of the items listed here are implemented, even in part, it should
allows us to make better use of the test-suite.

Several DejaGNU directives from the test files are currently ignored. In some
cases, those directives check that the language feature/optimization being
exercised by the tests is actually handled correctly. By ignoring them, we are
simply checking that `flang` (or the code produced by it) does not crash at
build/test time. In the case of the _compile_ tests where this is the case, we
could have situations where the test passes because the compilation succeeded,
not because the compiler actually did the right thing - for instance, the tests
in `gfortran/regression/vect` check if the code was correctly vectorized. We
could pass those tests just by failing to crash - not because `flang` actually
vectorized the code.

It is not clear how much effort would be involved in correctly handling all the
DejaGNU  directives.

### `dg-error` directive ###

The `dg-error` directive indicates that the test should fail to compile with a
particular error. Obviously, this is a `gfortran`-specific error. `flang` may
not have a direct equivalent i.e. it may produce a more general error message
(or maybe even a more specific one if `gfortran` is the one with the more
general error message). For now, when a`dg-error` is encountered, the test is
marked as `expect-error`. At test time, we only check if "some" error (that was
not a crash) occurred. This can cause false-negatives, particularly in the
OpenMP (and perhaps even OpenACC) tests. This is where some directives/clauses
are currently not implemented which results in a parse error (as opposed to the
triggering of a "not-yet-implemented" assertion) which is also deemed an "error",
thereby causing the test to pass.

#### `scan-tree-dump` directive ####

In the _compile_ tests, the `dg-final { scan-tree-dump* ...}` directives are
ignored. The `scan-tree-dump*` checks GCC's internal tree structure to ensure
that the specific language feature/optimization the test was meant to exercise
was handled correctly (see, for example, `regression/volatile_7.f90`).

The tests instruct GCC to write out the internal representation to file and scan
the file for the presence or absence of certain text. To capture the same
behavior here, we would need to parse and translate the internal representation
of GCC to an equivalent representation in LLVM IR.

### `target` directive ###

The `target` directive is used to restrict tests to run on certain
platforms/systems. Currently, the target directive is ignored entirely and the
tests are always run. Currently, the gfortran tests are only enabled on *nix on
x86-64 and aarch64 and ignoring the directive seems to be ok. As support for
more systems and architectures are added, these directives will need to be
handled correctly.
