#1: 
# availability
#2:
#hex('admin=1') = 0x61646D696E3D31
# a d m i n = 0
# 9c238d431d0f2e

#3: textbook_rsa_is_easy
#4: SPI
#5: 0.5 (A)
#6: v1.7.2
#7: perfect blue
#8: SolarWinds
#9: 2001:4c48:2:a341:204:75ff:fe7c:c901
#10: tail
#11: jemalloc
#12: aaaaaaaaaaaaaaaass4pdr0w
#13: ltrace
#14: 89EC5DC3
#15: just_a_basic_x86_code
#16: e
#17: smuggling
#18: this_is_jsfuck

#cd21{1n_1t_4nd_w1n_1t!}


# #include <stdio.h>
# int main() {
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# puts("hello\n");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# puts("hello2\n");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");

# }

def egcd(a, b):
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q, r = b//a, b%a
        m, n = x-u*q, y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
        gcd = b
    return gcd, x, y

def main():

    p = 97895746752372891871283422027043042061614577686530065446233616612333423604934011843200996680487677526879789179586786039582506950509293024631727783070830925085314167678657690804225291586344823854887079536113937037179906217782966484499059668578707953739801639859146969751084700674958632822922091962540104071107
    q = 108719296446064498008143737396004668132941036811186871376825445279508373750934080199890641861482658544845078428030961057373250464329294016345344451097991091038538954298752426636326436299942507818022252246943632901199425784112349575799549930600155586758230625799969689251054533889726886643889939907241885966637
    e = 65537
    ct = 9534253136837180343463316267358545731384733625253109532045949620182315193650675958090742196052854738610908779615078112746573354162378400699719906765433050694003554324613313237074810534764528108496909446295227457831456477267955873650135006449729874775897840044072326913892935515454141625792274255085020780255954978618532508049237577319755709709637515962534359078653590184914403962255630257139554819146009234217179432624111505682768200438271796107141098570628796900513138976107492166976162378470447447562275303831197174934445230880665933135980096360622624761929812481245950597156173863459145479543471550126911750170606

    # compute n
    n = p * q

    # Compute phi(n)
    phi = (p - 1) * (q - 1)

    # Compute modular inverse of e
    gcd, a, b = egcd(e, phi)
    d = a

    print( "n:  " + str(d) );

    # Decrypt ciphertext
    pt = pow(ct, d, n)
    print( pt )
    print(bytearray.fromhex(format(pt,'x')).decode('ascii'))

if __name__ == "__main__":
    main()