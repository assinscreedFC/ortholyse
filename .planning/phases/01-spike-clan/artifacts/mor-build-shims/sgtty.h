/* MinGW shim for legacy BSD <sgtty.h> — Ortholyse spike port.
   Only the symbols referenced by unix-clan cutt.cpp on the non-TERMIO path. */
#ifndef SHIM_SGTTY_H
#define SHIM_SGTTY_H

struct sgttyb {
    char  sg_ispeed;
    char  sg_ospeed;
    char  sg_erase;
    char  sg_kill;
    short sg_flags;
};

#ifndef TIOCGETP
#define TIOCGETP 0x40067408
#endif
#ifndef TIOCSETP
#define TIOCSETP 0x80067409
#endif

/* Legacy BSD terminal calls — unavailable on native Windows.
   mor runs in batch (non-tty) mode, so these fail gracefully. */
static inline int gtty(int fd, struct sgttyb *buf) {
    (void)fd;
    (void)buf;
    return -1;
}
static inline int stty(int fd, struct sgttyb *buf) {
    (void)fd;
    (void)buf;
    return -1;
}

#endif /* SHIM_SGTTY_H */
