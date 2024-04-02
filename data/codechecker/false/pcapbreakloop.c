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

#include <pcap/pcap.h>
#include <signal.h>
#include <stdatomic.h>

extern pcap_t *_Atomic p;

static void handler(int sig) {
    pcap_t *local_p = atomic_load_explicit(&p, memory_order_acquire);
    pcap_breakloop(local_p);
    (void)sig;
}

int setup_pcapbreakloop_handler(void) {
    return signal(SIGUSR1, handler) == SIG_ERR;
}
