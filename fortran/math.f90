module math
implicit none
    double precision, parameter :: pi = acos(-1d0)
    double precision, parameter :: sq2pi = sqrt(2d0*pi)
    double precision, parameter :: two_sq3 = 2d0*sqrt(3d0)
    
    integer :: n_integration_cuts = 50
contains
    ! Help-Functions
    subroutine read_arg(i_arg, parameter_value)
        integer, intent(in) :: i_arg
        double precision, intent(out) :: parameter_value
        character *100 :: buffer ! buffer to read in arguments from cmdline
        call getarg(i_arg, buffer)
        read(buffer,*) parameter_value
    end subroutine read_arg

    subroutine lognormal(x, mu, sig, lognormalval)
        double precision, intent(in) :: x, mu, sig
        double precision, intent(out) :: lognormalval
        lognormalval =&
            1d0 / (sq2pi*sig*x) * dexp(-0.5d0*(dlog(x/mu) / sig)**2)
    end subroutine lognormal

    subroutine gaussian(x, mu, sig, gaussianval)
        double precision, intent(in) :: x, mu, sig
        double precision, intent(out) :: gaussianval
        gaussianval =&
            1d0 / (sq2pi*sig) * dexp(-0.5d0*((x-mu) / sig )**2)
    end subroutine gaussian

    
    subroutine equipartition(x, mu, sig, equipartition_val)
        double precision, intent(in) :: x, mu, sig
        double precision, intent(out) :: equipartition_val
        equipartition_val =&
                    1d0/(sig*two_sq3)
    end subroutine equipartition

    subroutine one(x, mu, sig, oneval)
        double precision, intent(in) :: x, mu, sig
        double precision, intent(out) :: oneval
        oneval = 1d0
    end subroutine one
    
    double precision function func_one(q, p, Np)
        double precision, intent(in) :: q
        double precision, dimension(Np), intent(in) :: p
        integer, intent(in) :: Np
        
        func_one = 1d0
    end function func_one
    
    subroutine langevin_prob(psi, langevin, zero, p_langevin)
        double precision, intent(in) :: psi, langevin, zero
        double precision, intent(out) :: p_langevin

        double precision :: sin_psi, cos_psi
        double precision :: nominator, denominator
        sin_psi = sin(psi)
        cos_psi = cos(psi)
        nominator = langevin*exp(langevin*(1d0+cos_psi))
        denominator = (exp(2d0*langevin)-1d0)
        p_langevin = nominator/denominator
    end subroutine langevin_prob

    subroutine integrate_prob_distribution(pmu, psig, pmin, pmax, prob_dist,&
                                           probability)
        double precision, intent(in) :: pmu, psig, pmin, pmax
        external prob_dist
        double precision, intent(out) :: probability

        double precision :: abserr
        integer :: neval, ier, last
        integer, dimension(50) :: iwork
        double precision, dimension(200) :: work
        
        interface
            subroutine prob_dist(x, mu, sig, y)
                double precision, intent(in) :: x, mu, sig
                double precision, intent(out) :: y
            end subroutine
        end interface
        
        if (psig > 0d0) then
            call dqag (probability_function, pmin, pmax, 0d0, 1d-10, 6,&
                    probability, abserr, neval, ier, n_integration_cuts,&
                    4*n_integration_cuts, last, iwork, work)
        else
            probability = 1d0
        end if
        
        contains 
            double precision function probability_function(x)
                double precision :: x
                call prob_dist(x, pmu, psig, probability_function)
            end function probability_function

    end subroutine integrate_prob_distribution
    
    
    subroutine integrate_size_distribution(qval, p, Np, &
                pint, pmin, pmax, psig, &
                ff_function, prob_dist, ff_intensity)
        double precision, intent(in) :: qval
        double precision, dimension(Np), intent(in) :: p
        integer, intent(in) :: Np, pint
        double precision, intent(in) :: pmin, pmax, psig
        external ff_function
        external prob_dist
        double precision, intent(out) :: ff_intensity
        
        double precision :: abserr
        integer :: neval, ier, last
        integer, dimension(50) :: iwork
        double precision, dimension(200) :: work
        
        interface
            double precision function ff_function(q, p, Np)
                double precision, intent(in) :: q
                double precision, dimension(Np), intent(in) :: p
                integer, intent(in) :: Np
            end function
            
            subroutine prob_dist(x, mu, sig, y)
                double precision, intent(in) :: x, mu, sig
                double precision, intent(out) :: y
            end subroutine
        end interface
        
        if (psig > 0d0) then
            call dqag (size_dist_function, pmin, pmax, 0d0, 1d-10, 6,&
                    ff_intensity, abserr, neval, ier, n_integration_cuts,&
                    4*n_integration_cuts, last, iwork, work)
        else
            ff_intensity = ff_function(qval, p, Np)
        end if
        
        contains
            double precision function size_dist_function(x)
                double precision :: x
                double precision, dimension(Np) :: hp
                double precision :: prob, formfactor
                hp = p
                hp(pint) = x
                formfactor = ff_function(qval, hp, Np)
                call prob_dist(x, p(pint), psig, prob)
                
                size_dist_function = formfactor * prob
            end function size_dist_function
    end subroutine integrate_size_distribution


    subroutine integrate_two_size_distributions(qval, p, Np, &
                pint1, pmin1, pmax1, psig1, &
                pint2, pmin2, pmax2, psig2, &
                ff_function, prob_dist1, prob_dist2, ff_intensity)
        double precision, intent(in) :: qval
        double precision, dimension(Np), intent(in) :: p
        integer, intent(in) :: Np, pint1, pint2
        double precision, intent(in) :: pmin1, pmax1, psig1
        double precision, intent(in) :: pmin2, pmax2, psig2
        external ff_function
        external prob_dist1
        external prob_dist2
        double precision, intent(out) :: ff_intensity
        
        double precision :: abserr1, abserr2
        integer :: neval1, ier1, last1, neval2, ier2, last2
        integer, dimension(50) :: iwork1, iwork2
        double precision, dimension(200) :: work1, work2
        double precision, dimension(Np) :: help_params
        
        interface
            double precision function ff_function(q, p, Np)
                double precision, intent(in) :: q
                double precision, dimension(Np), intent(in) :: p
                integer, intent(in) :: Np
            end function
            
            subroutine prob_dist1(x, mu, sig, y)
                double precision, intent(in) :: x, mu, sig
                double precision, intent(out) :: y
            end subroutine
            
            subroutine prob_dist2(x, mu, sig, y)
                double precision, intent(in) :: x, mu, sig
                double precision, intent(out) :: y
            end subroutine
        end interface
        
        help_params = p
        if (psig1 > 0 .AND. psig2 > 0) then
            call dqag(integrate12, pmin1, pmax1, 0d0, 1d-10, 6,&
                    ff_intensity, abserr1, neval1, ier1, n_integration_cuts,&
                    4*n_integration_cuts, last1, iwork1, work1)

        else if (psig1 > 0) then ! means psig2 <= 0
            call dqag(integrate01, pmin1, pmax1, 0d0, 1d-10, 6,&
                    ff_intensity, abserr1, neval1, ier1, n_integration_cuts,&
                    4*n_integration_cuts, last1, iwork1, work1)

        else if (psig2 > 0) then ! means psig1 <= 0
            call dqag(integrate02, pmin2, pmax2, 0d0, 1d-10, 6,&
                    ff_intensity, abserr2, neval2, ier2, n_integration_cuts,&
                    4*n_integration_cuts, last2, iwork2, work2)

        else ! means psig1 and psig2 <= 0
            ff_intensity = ff_function(qval, p, Np)
        end if
        
        contains
            double precision function integrate12(x)
                double precision :: x
                double precision :: function_value, prob
                help_params(pint1) = x

                call dqag (integrate02, pmin2, pmax2, 0d0, 1d-10, 6,&
                    function_value, abserr2, neval2, ier2, n_integration_cuts,&
                    4*n_integration_cuts, last2, iwork2, work2)
                call prob_dist1(x, p(pint1), psig1, prob)

                integrate12 = function_value * prob
            end function integrate12
            
            double precision function integrate01(x)
                double precision :: x
                double precision :: function_value, prob
                help_params(pint1) = x

                function_value = ff_function(qval, help_params, Np)
                call prob_dist1(x, p(pint1), psig1, prob)

                integrate01 = function_value * prob
            end function integrate01
            
            double precision function integrate02(x)
                double precision :: x
                double precision :: function_value, prob
                help_params(pint2) = x

                function_value = ff_function(qval, help_params, Np)
                call prob_dist2(x, p(pint2), psig2, prob)

                integrate02 = function_value * prob
            end function integrate02
    end subroutine integrate_two_size_distributions

    subroutine twodim_integral_variable_bounds(xmin, xmax, &
                                               ymin_func, ymax_func, &
                                               p, Np, &
                                               integrand_func, integrand_res)
        double precision, intent(in) :: xmin, xmax
        external ymin_func
        external ymax_func
        double precision, dimension(Np), intent(in) :: p
        integer, intent(in) :: Np
        external integrand_func
        double precision, intent(out) :: integrand_res
        
        double precision :: abserr1, abserr2
        integer :: neval1, ier1, last1, neval2, ier2, last2
        integer, dimension(50) :: iwork1, iwork2
        double precision, dimension(200) :: work1, work2
        double precision, dimension(Np+1) :: help_params
        
        interface
            double precision function ymin_func(x, p, Np)
                double precision, intent(in) :: x
                double precision, dimension(Np), intent(in) :: p
                integer, intent(in) :: Np
            end function
            
            double precision function ymax_func(x, p, Np)
                double precision, intent(in) :: x
                double precision, dimension(Np), intent(in) :: p
                integer, intent(in) :: Np
            end function
            
            double precision function integrand_func(x, y, p, Np)
                double precision, intent(in) :: x, y
                double precision, dimension(Np), intent(in) :: p
                integer, intent(in) :: Np
            end function
        end interface
        
    
        help_params(1:Np) = p
        help_params(Np+1) = 0d0
        call dqag(integrate12, xmin, xmax, 0d0, 1d-10, 6,&
                integrand_res, abserr1, neval1, ier1, n_integration_cuts,&
                4*n_integration_cuts, last1,&
                iwork1, work1)
        
        contains
            double precision function integrate12(x)
                double precision :: x
                double precision :: ymin, ymax
                ymin = ymin_func(x, p, Np)
                ymax = ymax_func(x, p, Np)
                help_params(Np+1) = x
                call dqag (integrate02, ymin, ymax, 0d0, 1d-10, 6,&
                    integrate12, abserr2, neval2, ier2, n_integration_cuts,&
                    4*n_integration_cuts, last2,&
                    iwork2, work2)
            end function integrate12
            
            double precision function integrate02(y)
                double precision :: y
                double precision :: x
                
                x = help_params(Np+1)
                integrate02 = integrand_func(x, y, p, Np)
            end function integrate02
    end subroutine twodim_integral_variable_bounds
    
    subroutine get_cutoff_gaussian(mu, sig, left_cutoff, right_cutoff)
        double precision, intent(in) :: mu, sig
        double precision, intent(out) :: left_cutoff, right_cutoff
        
        if (sig > 0d0) then
            left_cutoff = mu - 5d0*sig
            right_cutoff = mu + 5d0*sig
        else
            left_cutoff = 0d0
            right_cutoff = 0d0
        end if
    end subroutine get_cutoff_gaussian

    subroutine get_cutoff_lognormal(mu, sig, left_cutoff, right_cutoff)
        double precision, intent(in) :: mu, sig
        double precision, intent(out) :: left_cutoff, right_cutoff
        
        double precision :: prob_integrated
        
        double precision :: abserr
        integer :: neval, ier, last
        integer, dimension(50) :: iwork
        double precision, dimension(200) :: work
        
        if (sig > 0d0) then
            left_cutoff = mu*exp(-5*sig)
            right_cutoff = mu*exp(-sig**2) + sig*mu
            prob_integrated = 0d0
            ! Shift right cutoff of integral, until lognormal distribution
            ! integrates to 1 with 1d-6 tolerance.
            do while (abs(prob_integrated-1d0) > 1d-6)
                call dqag(lognormal_function, left_cutoff, right_cutoff, &
                          0d0, 1d-10, 6, prob_integrated, abserr, neval, &
                          ier, n_integration_cuts, 4*n_integration_cuts, last, iwork, work)
                right_cutoff = right_cutoff + sig*mu
            end do
        else
            left_cutoff = 0d0
            right_cutoff = 0d0
        end if
        contains
            double precision function lognormal_function(x)
                double precision :: x
                call lognormal(x, mu, sig, lognormal_function)
            end function lognormal_function
    end subroutine get_cutoff_lognormal
    
    subroutine mean(x, Nx, meanx)
        double precision, dimension(Nx), intent(in) :: x
        integer, intent(in) :: Nx
        double precision, intent(out) :: meanx
        
        meanx = sum(x) / Nx
    end subroutine mean
    
    subroutine simple_linear_fit(x, y, Nx, slope, intercept)
        double precision, dimension(Nx), intent(in) :: x, y
        integer, intent(in) :: Nx
        double precision, intent(out) :: slope, intercept
        
        double precision :: mean_xy, mean_x, mean_y, mean_x2
        
        call mean(x, Nx, mean_x)
        call mean(y, Nx, mean_y)
        call mean(x*y, Nx, mean_xy)
        call mean(x*x, Nx, mean_x2)
        
        slope = (mean_xy-mean_x*mean_y) / (mean_x2-mean_x**2)
        intercept = mean_y - slope*mean_x
    end subroutine simple_linear_fit
    
    subroutine get_interpolated_value(x, y, xval, Nx, yval)
        double precision, dimension(Nx), intent(in) :: x, y
        double precision, intent(in) :: xval
        integer, intent(in) :: Nx
        double precision, intent(out) :: yval
        
        integer :: ix
        double precision :: x_left, x_right, y_left, y_right
        
        if (xval <= x(1)) then
            yval = (y(2)-y(1))*(xval-x(1))/(x(2)-x(1)) + y(1)
            return
        end if
        
        if (xval >= x(Nx)) then
            yval = (y(Nx)-y(Nx-1))*(xval-x(Nx))/(x(Nx)-x(Nx-1)) + y(Nx)
            return
        end if
        
        do ix=1, Nx
            if (x(ix) > xval) then
                x_left = x(ix-1)
                x_right = x(ix)
                y_left = y(ix-1)
                y_right = y(ix)
                exit
            end if
        end do
        yval = (y_right-y_left)*(xval-x_right)/(x_right-x_left) + y_right
    end subroutine get_interpolated_value
end module math
