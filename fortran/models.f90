module models
use math
implicit none

double precision, parameter :: kB = 1.38064852d-23 ! J/K
double precision, parameter :: muB = 9.274009994d-24 ! J/T
double precision, parameter :: muB_by_kB = 0.6717140430498562 ! K/T

contains
    double precision function langevin(B, p, Np)
        !Langevin: Spherical Homogenously Magnetized Particle with large moment
        double precision, intent(in) :: B
        double precision, dimension(Np), intent(in) :: p
        integer, intent(in) :: Np

        double precision :: Ms, xi, x
        Ms = p(1)
        xi = p(2)

        if (abs(B) > 1e-9) then
            x = xi*B
            langevin = Ms * (1d0/tanh(x) - 1d0/x)
        else
            langevin = 0d0
        end if
    end function langevin

    double precision function langevin_mu(B, p, Np)
        double precision, intent(in) :: B
        double precision, dimension(Np), intent(in) :: p
        integer, intent(in) :: Np
        double precision :: Ms, mu, T, xi

        Ms = p(1)
        mu = p(2)
        T = p(3)

        xi = mu/T*muB_by_kB
        langevin_mu = langevin(B, (/Ms, xi/), 2)
    end function langevin_mu

    subroutine magnetization_mu(B, Ms, mu, T, sig_mu, NB, Magnetization)
        double precision, dimension(NB), intent(in) :: B
        double precision, intent(in) :: Ms, mu, T, sig_mu
        integer, intent(in) :: NB
        double precision, dimension(NB), intent(out) :: Magnetization

        integer, parameter :: Np = 3
        double precision, dimension(Np) :: p

        double precision :: mu_min, mu_max
        integer :: iB

        call get_cutoff_lognormal(mu, sig_mu, mu_min, mu_max) 
        
        p = (/Ms, mu, T/)
        !$omp parallel
        !$omp do
        do iB=1, NB
            call integrate_size_distribution(B(iB), p, Np, &
                        2, mu_min, mu_max, sig_mu, &
                        langevin_mu, lognormal,&
                        Magnetization(iB))
        end do
        !$omp end do
        !$omp end parallel
    end subroutine magnetization_mu
end module models

