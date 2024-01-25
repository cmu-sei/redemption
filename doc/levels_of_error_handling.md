# Levels of Error Handling

<legal>
'Redemption' Automated Code Repair Tool
Copyright 2023, 2024 Carnegie Mellon University.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
INFRINGEMENT.
Licensed under a MIT (SEI)-style license, please see License.txt or
contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public
release and unlimited distribution.  Please see Copyright notice for
non-US Government use and distribution.
This Software includes and/or makes use of Third-Party Software each
subject to its own license.
DM23-2165
</legal>

This document dictates several levels of error-handling, where each level imposes extra restrictions, and offers more guarantees. The job of error-handling, and the default level are the responsibility of the developer, although the programming language they use can help, as well as the error-handling technology they choose to use with the language.

Programs can be divided up into functions, and each function could have its own level of error handling.  You could define a program's error-handling level by the minimum of the error-handling levels of its functions, or the maximum, or the mean.

## Prevention and Detection

Some errors can be easily prevented. For example, in this function:

``` c
void f(char* s) {
  printf("String is %s\n", s);
}
```

The `s` pointer could be NULL. Passing a NULL pointer to `printf()` is undefined behavior, although many platforms handle it gracefully. Glibc (used by gcc and clang) will print `(null)`.

This error can be easily prevented with a null check:

``` c
void f(char* s) {
  if (s == NULL) {
    /* Handle error */
  }
  printf("String is %s\n", s);
}
```

Provided that the `/* Handle error */` is replaced with code that does not allow the function to continue, it adequately prevents null dereference.

Other errors can not be easily prevented, but can be easily detected. For example:

``` c
void f(double d) {
  printf("The tangent of %f is %f\n", d, tan(d));
}
```

If `d` is close to `PI*n/2` where `n` is an odd number, then `tan(d)` will produce a value that cannot be represented by a double. In ISO C, this behavior is undefined, but in IEEE 754, this will produce the value `Infinity` or `-Infinity`.  This can be detected after the fact.

``` c
void f(double d) {
  double tan_d = tan(d);
  if (tan_d == Infinity || tan_d == -Infinity) {
    /* Handle error */
  }
  printf("The tangent of %f is %f\n", d, tan(d));
}
```

Most errors can be reliably prevented, and many errors that cannot be reliably prevented can be reliably detected...there are very few errors that are neither preventable nor detectable.  One example of such an error is a freed pointer in C or C++.  Dereferencing a freed pointer is undefined behavior, and yet there is no standard way to know if a pointer has been freed.   Consequently, the C community assumes that all pointers passed to functions are either valid non-freed pointers, or NULL, and any good C program will clearly constrain any invalid pointers.  C coding standards also recommend disposing of freed pointers promptly, such as CERT rule MEM02-C.

## Error-Handling Levels
### Undefined Behavior

Undefined behavior is officially defined in ISO C as "behavior, upon which this Standard imposes no constraints". That is, a machine executing undefined behavior is free to do anything.  Many security vulnerabilities (eg memory safety, concurrency safety) arise from undefined behavior. This freedom makes undefined behavior difficult to predict, as it may be treated specially by the program's compiler, CPU, and operating system.

Java, Python, and Rust do not have undefined behavior....you must use JNI code, or 'unsafe' Rust.

#### 1. No Error Detection or Prevention

This level, the lowest available, indicates a program that neither detects nor prevents errors. Forbidden by CERT recommendation EXP12-C.

This is the default for C & C++. Most C/C++ errors that are neither detected nor prevented result in undefined behavior.

##### Example: Reading a File in C

In the following code example, there is no detection that `fopen()`, `fgets()`, or `fclose()` succeed. If `fopen()` fails, it will return NULL, which means that `fgets()` and `fclose()` receive NULL pointers for their stream argument, which produces undefined behavior.  If `fopen()` succeeds, but `fgets()` fails, then it fails to set `s` to a proper null-terminated byte string, in which case, printing the contents of `s` is undefined behavior.

``` c
const size_t Len = 80;

void f(char* name) {
  char* s[Len];
  FILE* f = fopen(name, "r");
  fgets( s, Len, f);
  fclose(f);
  printf("File %s starts with %s\n", name, s)
}
```

### Preventing Undefined Behavior
#### 2. Errors Detected but neither Prevented nor Handled

This level indicates that a program detects error conditions but does not prevent the undefined behavior that results from them.

##### Example: Reading a File in C

In the following code example, the calls to `fopen()`, `fgets()`, and `fclose()` all have their return values checked, and a line is printed to standard error if any call fails. However, after an error is reported, the program continues, which produces the same undefined behaviors as the previous example. This program does have the advantage that if undefined behavior occurs, an error is at least reported, which is useful for debugging.

``` c
const size_t Len = 80;

void f(char* name) {
  char* s[Len];
  FILE* f = fopen(name, "r");
  if (NULL == f) {
    fprintf(stderr, "Error opening %s\n", name);
  }
  if (NULL == fgets( s, Len, f)) {
    fprintf(stderr, "Error reading %s\n", name);
  }
  if (NULL == fclose(f)) {
    fprintf(stderr, "Error closing %s\n", name);
  }
  printf("File %s starts with %s\n", name, s)
}
```

#### 3. Unexpected Errors Terminate

This level indicates that any error the program may encounter leads to immediate abnormal termination.  In fact, the program could do anything that prevents normal continuation, such as throwing an exception, or jumping back to a known good state...but termination is the easiest way to prevent normal continuation in most languages.

This is the default for uncaught thrown exceptions, which are supported by Java and Python. It is alto the default for for failed assertions, which are supported by most modern languages, including C, C++, Java, Python, and Rust.

Command-line programs must achieve this level at a minimum in order to be considered production-ready. They should have some simple method of reporting errors, and they must prevent undefined behavior from occurring.  (They may leave external resources held...see the next section for details. Ideally they would document this flaw.)

##### Example: Reading a File in C

In the following code example, the calls to `fopen()`, `fgets()`, and `fclose()` all have their return values checked, and if any one fails, the program immediately terminates. This prevents undefined behavior. It also prevents recovering from any error. No error is reported by the program, but a debugger can easily indicate which line failed. See the previous code example for error reporting.

``` c
const size_t Len = 80;

void f(char* name) {
  char* s[Len];
  FILE* f = fopen(name, "r");
  if (NULL == f) {
    abort();
  }
  if (NULL == fgets( s, Len, f)) {
    abort();
  }
  if (NULL == fclose(f)) {
    abort();
  }
  printf("File %s starts with %s\n", name, s)
}
```

### Resource Cleanup

Every program has resources which it must dynamically claim and may release. Some resources, such as memory, and open files, are released by the operating system when the program exits, and other resources, such as external lock files, are not. Any resource reclaimed by the operating system is an 'internal' resource, with other resources being 'external'.

Any program in level 3 "Unexpected Errors Terminate" need not clean up any resources.

C++ programs can clean up internal and external resources using RAII. Java and Python can clean up resources when exceptions are thrown using 'finally' (whether or not the exceptions are caught). Java, Python, and Rust do not explicitly support RAII, but they do have 'AutoCloseable' classes. These classes represent resources that must be explicitly released, and each language supports syntax to automatically release such objects after a block of code completes. (See Java's try-with-resources, and Python's `with` statement for more details)

Since C lacks exceptions or RAII, C functions beyond a small level of complexity must rely on goto chains, even though goto is still considered harmful. For more information, see CERT recommendation MEM12-C.  C typically uses return values to indicate errors that transcend one function. Rust doubles down on this strategy using the `Return<>` class.

##### Example: Lock File in C

The following code example creates an empty 'lock' file, which lasts for the lifetime of the program, and is removed when the program exits. However, if any error occurs in one of the subsequent function calls, the program may exit without removing the lock file. Likewise, the `f` file may also not be closed properly if an error occurs in the `fgets()` function.

``` c
const size_t Len = 80;

void f(char* name) {
  FILE* lock_file = fopen("lock", "w");
  if (NULL == lock_file) {
    abort();
  }
  if (NULL == fclose(lock_file)) {
    abort();
  }

  char* s[Len];
  FILE* f = fopen(name, "r");
  if (NULL == f) {
    abort();
  }
  if (NULL == fgets( s, Len, f)) {
    abort();
  }
  if (NULL == fclose(f)) {
    abort();
  }
  printf("File %s starts with %s\n", name, s)

  if (0 == remove(lock_file)) {
    abort();
  }
}
```

#### 4. External Resources cleaned up

Any program that properly cleans up external resources upon errors is in at least this level.  This also applies to any programs that have no external resources.

Ideally, every command-line program would achieve this level, and not leave external resources to be cleaned up by the user when errors occur.

##### Example: Lock File in C

The following code example creates an empty 'lock' file, which lasts for the lifetime of the program, and is removed when the program exits. The program also tries to remove the lock file if any error occurs elsewhere, and consequently the program cleans up all external resources.  However, the `f` file may also not be closed properly if an error occurs in the `fgets()` function.

``` c
const size_t Len = 80;

void remove_lock_file(FILE* lock_file) {
  if (0 == remove(lock_file)) {
    abort();
  }
}

void f(char* name) {
  FILE* lock_file = fopen("lock", "w");
  if (NULL == lock_file) {
    abort();
  }
  if (NULL == fclose(lock_file)) {
    abort();
  }

  char* s[Len];
  FILE* f = fopen(name, "r");
  if (NULL == f) {
    remove_lock_file(lock_file);
    abort();
  }
  if (NULL == fgets( s, Len, f)) {
    remove_lock_file(lock_file);
    abort();
  }
  if (NULL == fclose(f)) {
    remove_lock_file(lock_file);
    abort();
  }
  printf("File %s starts with %s\n", name, s)

  remove_lock_file(lock_file);
}
```

#### 5. Internal Resources cleaned up

Any program that properly cleans up both internal and external resources upon errors is in at least this level.

##### Example: Lock File in C with Goto Chain

The following code example creates an empty 'lock' file, which lasts for the lifetime of the program, and is removed when the program exits. The program also tries to remove the lock file if any error occurs elsewhere. Likewise, the program tries to close the `f` file if any errors occur while the file is open. Consequently, the program cleans up all external resources.

Note that this program no longer calls `abort()` if an error occurs. It instead returns true if successful and false is any error occurs.

``` c
const size_t Len = 80;

bool f(char* name) {
  bool retval = false;
  FILE* lock_file = fopen("lock", "w");
  if (NULL == lock_file) {
    goto end;
  }
  if (NULL == fclose(lock_file)) {
    goto end;
  }

  char* s[Len];
  FILE* f = fopen(name, "r");
  if (NULL == f) {
    goto remove_lock_file;
  }
  if (NULL == fgets( s, Len, f)) {
    goto close_f;
  }

  printf("File %s starts with %s\n", name, s)

  retval = true;
close_f:
  fclose(f);
remove_lock_file:
  remove(lock_file);
end:
  return retval;
}
```

### Recovery

Before this level, every program would either terminate immediately upon error (perhaps after some resource cleanup), or suffer from undefined behavior. The subsequent levels suggest alternate techniques from recovering from errors.

Note that programs that support alternate recovery mechanisms may still decide to terminate abnormally. This can happen if they detect bugs in themselves or attacks, in which case shutting down prematurely may be preferred to being successfully hacked.

#### Expected vs Unexpected Errors

As programs grow larger, the number of potential error conditions increases quickly. For example, in C, every call to `malloc()` presents an error condition; what if `malloc()` returns NULL?  Likewise, every addition, subtraction, and multiplication operation introduces the possibility of wrapping or overflow.  In Java, many functions that call many different sub-functions may have a large number of exceptions to catch, or declare that it may throw. (Some systems will create their own exception class, and use chaining to encapsulate any thrown exception into its own exception class. IOException and SQLException are two such example exception classes that encompass many different error conditions).  Consequently, we partition errors into expected errors and unexpected errors. Expected errors are errors for which we have a known, documented recovery mechanism, and unexpected errors are errors which lack any such mechanism.  In most programs, most errors are unexpected.

#### Recovery Schemes

Recovery is most easily accomplished with try-catch statements.  However try-catch statements are not supported in C. C does have some technologies for error recovery, such as `setjmp()` and `longjmp()`, however the most popular recovery method in C is to use function return values, where a specific value (such as NULL or `EOF`) indicates an error and any other value indicates success.  This requires calling functions to inspect a function's return value for its error values and act accordingly.  This mechanism has been copied by Rust in its `Result<>` class.

As noted above, many command-line utilities have no special recovery schemes, apart from cleaning up resources. Printing an error message, and terminating are sufficient for such utilities, with the expectation that the user can re-invoke the utility after dealing with the error message. Such utilities also tend to be short-lived and terminate quickly after fulfilling their function.  This minimizes the complexity of resource cleanup, and keeps the program simple.

However, most programs are not command-line utilities. They may expect to run for a long time. They may also lack a console, or any visible error stream.  They may, or may not, have alternate interfaces for notifying a user of errors.  We can speak of one common error recovery design pattern.

##### Event-Based Programming

An event-based program is one whose main lifetime consists of receiving events and handling them. The program, in a nutshell, will have a lifetime of the following:

After initialization, which includes setting up the event queue, the system enters a while loop. This loop only quits if the next event received indicates that it should shut down. Many systems lack a `shut_down()` function, and so there may be no intended function, no event mandates shutdown, and the program loops forever.  Likewise, as long as the event queue remains empty, the program may `yield()`; that is, sleep or allow other processes on the platform to resume. This program handles events as they come along.

In particular, there is only one catch clause in the entire program, which catches any error thrown while processing events. Note that event handling should release any resources acquired during event processing, so that any exception thrown can be recovered during this loop. Only `handle_event()` may throw exceptions that get caught. Any exceptions thrown be `start_up()` or `shut_down()` may terminate the program (while cleaning up resources), or the `start_up()` procedure may also provide its own recovery mechanism. Ideally, the other functions never throw exceptions.

``` cpp
Event_Queue event_queue;

void main() {
  start_up(); /* initializes event_queue among other things */
  while (true) {
    if (!event_queue.has_events()) {
      yield();
    } else {
      Event e = event_queue.pop();
      if (e.indicates_shut_down()) {
        break;
      }
      try {
        handle_event(e);
      } catch (Exception x) {
        report_exception(x);
      }
    }
  }
  shut_down();
}
```

###### Example: Web Server

Event-based programming actually occurs in many domains.  A web server is one example of event-based programming. The `start_up()` procedure sets up the TCP port, and there is usually no `shut_down()` procedure. The `event_queue` contains HTTP requests, and the `handle_event()` function will traditionally delegate requests based on the protocol...one function for `GET` requests, one for `POST` requests, and so on. It will then take the HTML response generated by the appropriate delegation functions and send the response back down the socket. Finally, the `report_exception()` function will generate an appropriate HTML response based on the error and sent the response down the socket. Typically this response will be an "internal server error".

#### 6. Unexpected Exceptions Recovered after Setup

This is the typical level for event-based programs. They provide a recovery mechanism inside the event loop which handles all unexpected exceptions (the `report_exception()` function). Event handlers are still expected to clean up after themselves, and this enables the event-based program to continue executing properly after error recovery.

In this level, the `start_up()` function need provide no error recovery; it may terminate, after cleaning up external resources and providing a basic error message.

##### Example: Grep

While it is a command-line utility, the `grep` command can also serve as an example of event-based programming. The `grep(1)` utility takes a regular expression to search for, and a list of one or more files to search. It then reports each line in each file that contains text that matches the regular expression. In particular, if one of the files passed to `grep` cannot be opened, then `grep` should emit a suitable error message (to standard error) and continue operating with the next file.

For `grep`, the `start_up()` procedure compiles the regular expression, and processes any other command-line arguments. There is a `shut_down()` procedure, as `grep` must terminate normally when the list of input files is exhausted, but the `shut_down()` method need do nothing. The `event_queue` contains file names, provided on the command line, and the `handle_event()` function opens each file and prints out each line that contains a match for the regular expression. Finally, the `report_exception()` function will print an appropriate error response, which typically arises from opening, reading, or closing a file.

Note that while `grep` can recover from an invalid filename, it need not recover from initialization errors, such as an invalid regular expression.

#### 7. All Unexpected Exceptions Recovered

In this level, all unexpected exceptions must be handled by some generic recovery mechanism. This can apply to event-based programs or non-event-based programs.

##### Example: Graphical User Interface (GUI)

A GUI is one such example of event-based programming. The `start_up()` procedure sets up the GUI's window, which can consist of various widgets. There are many classes of widgets; some widgets display text, others provide buttons, and others contain more widgets, and so on. There might be a menu-bar widget and toolbar widget. The `shut_down()` procedure closes the GUI, and is typically invoked by a "Quit" button or menu item. The `event_queue` can consist of keyboard presses, mouse button presses, or mouse movements. On smartphones, the `event_queue` can contain various touch gestures.  Typically most such events are not interesting to the GUI, and part of the job done by `start_up()` is to register which events are interesting and should be handled. For example, clicking the primary mouse button in a text area may do nothing, but in a button, it should "activate" the button, performing the button's action. The `handle_event()` function determines if the GUI is interested in the current event, and which delegate function to call. Finally, the `report_exception()` button might display a dialog box with an appropriate message describing the exception.

While most GUIs in Linux can be invoked from the command line, and can terminate with errors upon initialization, typically a GUI program will be invoked from another GUI. For example, many Windows programs are invoked from the Windows Start Menu. This means they have no visible console. In these cases, a `report_exceptions()` function (or a similar analogue) should also be used to report exceptions that occur during program setup. While the GUI might terminate after reporting the exception, the exception reporter will typically have to display an error dialog before the GUI window has even been rendered.

### Expected Errors

All programs in previous levels have a (typically) large supply of unexpected exceptions. In these levels, the number and type of unexpected exceptions is empty. This is accomplished by extensively documenting all possible errors and providing explicit mechanisms to recover from, or prevent each error. This is slow, demanding work, and is typically done for only the most safety-critical programs.

#### 8. No Unexpected Exceptions (after Setup)

This level applies only to event-based programming. In this level, the unexpected exceptions that can occur in the event loop are minimized or eliminated. However, exceptions can still occur during the startup or shutdown phases.

This is the only level that does not require the immediately previous level. A program can comply with level 8 but not comply with level 7, if it has minimal event-handling errors, but may abort (with proper cleanup) on startup or shutdown errors.

##### Example: Embedded Avionics Program

Embedded programs are common examples of event-based programming. Typically the program lives on a computer with no console, or perhaps in a system of computers buried in some non-computing technology, such as a car or airplane. In such programs terminating abnormally is not acceptable, typically rebooting is the most drastic action the program can take. The events the embedded program must handle represent real-world events, such as "the user turned the ignition key".  In these cases, the most that the `report_exception()` can do is log the exception, perhaps in a local file system, to be inspected by an auto mechanic later.

Because the choices for handling errors is so poor, embedded code should typically operate at the highest levels. This means, among other things, minimizing the number and type of errors that may occur. Avionics code, for example, is typically allowed to allocate memory dynamically (using `malloc()`) only during the `start_up()` function, before the plan has left the ground. After take-off, allocating or freeing dynamic memory is forbidden, which eliminates a large class of memory safety errors.

#### 9. No Unexpected Exceptions

This level applies to all code, but is most prominent in event-based programming. In this level, the unexpected exceptions that can occur anywhere in the code are minimized or eliminated.

##### Example: Embedded Program, General

Embedded programs are common examples of event-based programming. A program might have no more interface than a speaker that can beep, but do nothing else. Thus an embedded program can only provide a particular beep sequence to indicate that all is not right with the program. Consequently, errors must be minimized. Typically such devices will have an external glossary of "beep codes", where each particular pattern of beeps indicates a distinct problem.

The MISRA-C (2004) standard forbids several standard C functions that can lead to errors, including `malloc()` (Rule 20.4), `setjmp()` and `longjmp()` (Rule 20.7), I/O functions defined in `stdio.h` (Rule 20.9), among others. These rules are particular for embedded code, and CERT C does not forbid these functions (although it does contain many guidelines on their proper usage).
