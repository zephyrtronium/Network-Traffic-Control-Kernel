#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/ether.h>
#include <netpacket/packet.h>
#include <net/if.h>
#include <sys/ioctl.h>

#define ETH_P_CUSTOM 0x88B5  // Custom EtherType for filtering
#define PAYLOAD_OFFSET 14    // Offset for unique identifier (after Ethernet header)

int main(int argc, char* argv[]) {
    if (argc <= 2) {
        perror("send_raw_eth_2 interface num_packet [start]");
        exit(EXIT_FAILURE);
    }
    char *iface = argv[1];
    int NUM_PACKETS = atoi(argv[2]);
    uint16_t start = 0;
    if (argc > 3) {
        start = atoi(argv[3]);
    }
    int sockfd;
    struct ifreq ifr;
    struct sockaddr_ll sa;
    unsigned char packet[1024];

    // Create a raw socket
    sockfd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_CUSTOM));
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // Get interface index
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, iface, IFNAMSIZ - 1);
    if (ioctl(sockfd, SIOCGIFINDEX, &ifr) < 0) {
        perror("ioctl");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // Set up sockaddr_ll
    memset(&sa, 0, sizeof(sa));
    sa.sll_ifindex = ifr.ifr_ifindex;
    sa.sll_halen = ETH_ALEN;
    memset(sa.sll_addr, 0xFF, ETH_ALEN); // Broadcast or set a custom MAC

    // Build Ethernet frame
    struct ethhdr *eth = (struct ethhdr *)packet;
    memset(eth->h_dest, 0xAA, ETH_ALEN); // Dummy destination MAC (AA:AA:AA:AA:AA:AA)
    memset(eth->h_source, 0xBB, ETH_ALEN); // Dummy source MAC (BB:BB:BB:BB:BB:BB)
    eth->h_proto = htons(ETH_P_CUSTOM); // Custom EtherType

    // Pointer to the payload section
    uint16_t *packetIdentifier = (uint16_t *)(packet + PAYLOAD_OFFSET);

    // Send packet with unique identifiers
    for (uint16_t i = 0; i < NUM_PACKETS; i++) {
        // Directly assign the identifier
        *packetIdentifier = htons(start + i); // Use htons to ensure network byte order

        // Fill the rest of the payload with a pattern (optional)
        memset(packet + PAYLOAD_OFFSET + sizeof(uint16_t), 0x42, 
               sizeof(packet) - PAYLOAD_OFFSET - sizeof(uint16_t));

        // Send packet
        if (sendto(sockfd, packet, sizeof(packet), 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
            perror("sendto");
            close(sockfd);
            exit(EXIT_FAILURE);
        }
    }

    printf("Dummy packets sent.\n");

    close(sockfd);
    return 0;
}
