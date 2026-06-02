/* MinGW shim for <sys/ioctl.h> — Ortholyse spike port.
   ioctl is unavailable on native Windows; mor runs in batch (non-tty) mode,
   so terminal queries simply fail gracefully (return -1). */
#ifndef SHIM_SYS_IOCTL_H
#define SHIM_SYS_IOCTL_H

#include <stdarg.h>

static inline int ioctl(int fd, unsigned long request, ...) {
    (void)fd;
    (void)request;
    return -1; /* not a terminal / unsupported — batch mode */
}

#endif /* SHIM_SYS_IOCTL_H */
