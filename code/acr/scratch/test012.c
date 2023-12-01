
// <legal>
// 'Redemption' Automated Code Repair Tool
// 
// Copyright 2023 Carnegie Mellon University.
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

int printf(const char *format, ...);

int main() {

    #define mac_add(x, y) ((x) + (y))
    int x=333, y=444;
    int sum = mac_add(x, y);
    printf("sum = %d\n", sum);

    #define mac_mul(x, y) ((x)*(y))
    int aa=2, bb=3, cc=5;
    int prod = mac_mul(aa, mac_mul(bb, cc));
    printf("prod = %d\n", prod);

    #define mac_bad_add(x, y) x + y*111
    int zz = mac_bad_add(x=y, 555) * 999;
    printf("zz = %d\n", zz);

    #define mac_concat_id(x, y) x ## y
    int goat = 42;
    mac_concat_id(go,at) = 777;
    printf("goat = %d\n", goat);
    return 0;
}
